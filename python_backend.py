#!/usr/bin/env python3
"""
print-wrapper — CUPS Backend (Hardened Production Ready)

Architecture: Host-based, Configurable Fail-Open/Fail-Closed strategy.
"""

import os
import sys
import json
import logging
import traceback
import subprocess
import urllib.request
import urllib.error
import re
from dataclasses import dataclass, field

# --- CONFIGURATION ---

ENABLE_API = True  # ИСПРАВЛЕНО: Проверка политики включена по умолчанию
API_URL = "http://localhost:8080/api/print"

# Стратегия безопасности при отказе API.
# "OPEN" — разрешить печать (Fail-Open),
# "CLOSED" — заблокировать (Fail-Closed, strict compliance)
API_FAIL_STRATEGY = "CLOSED"

# Белый список легитимных схем бэкендов CUPS для защиты от Path Traversal
ALLOWED_SCHEMES = {"usb", "socket", "ipp", "ipps", "http", "https", "lpd", "dnssd", "snmp", "hp"}

# Максимально допустимое количество копий для защиты от DoS/истощения бумаги
MAX_COPIES_LIMIT = 1000

# Setup Logging to stderr (Captured by CUPS in /var/log/cups/error_log)
logger = logging.getLogger("cups-backend")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


@dataclass
class JobInfo:
    job_id: str
    user_name: str
    printer_name: str
    title: str
    copies: str
    options: dict = field(default_factory=dict)
    file_path: str = ""
    device_uri: str = ""


def parse_cups_options(options_str: str) -> dict:
    """
    ИСПРАВЛЕНО: Корректный парсинг опций CUPS с учетом кавычек и пробелов.
    Пример: job-name="My Document" media=A4 -> {'job-name': 'My Document', 'media': 'A4'}
    """
    options = {}
    if not options_str:
        return options

    # Регулярное выражение для поиска пар key=value с учетом одинарных/двойных кавычек и флагов
    pattern = re.compile(
        r'([^=\s]+)=(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))|([^\s]+)'
    )

    for match in pattern.finditer(options_str):
        groups = match.groups()
        if groups[4]:  # Флаг без значения (например, 'landscape')
            options[groups[4]] = True
        else:
            key = groups[0]
            # Выбираем значение из той группы, которая сработала (в кавычках или без)
            val = groups[1] or groups[2] or groups[3]
            options[key] = val

    return options


def parse_job_params(argv: list) -> JobInfo:
    if len(argv) < 5:
        raise ValueError(f"Invalid argument count: {len(argv)}. Expected >= 5.")

    job_id = argv[1]
    user_name = argv[2]
    title = argv[3]
    copies = argv[4]
    raw_options = argv[5] if len(argv) > 5 else ""
    file_path = argv[6] if len(argv) > 6 else ""

    parsed_options = parse_cups_options(raw_options)

    printer_name = os.environ.get("PRINTER", "UNKNOWN_PRINTER")
    device_uri = os.environ.get("DEVICE_URI", "stub://localhost")

    return JobInfo(
        job_id=job_id,
        user_name=user_name,
        printer_name=printer_name,
        title=title,
        copies=copies,
        options=parsed_options,
        file_path=file_path,
        device_uri=device_uri,
    )


def validate_job_info(job: JobInfo) -> tuple[bool, str]:
    if not job.job_id or not job.job_id.isdigit():
        return False, f"Invalid Job ID format: '{job.job_id}'"

    # ИСПРАВЛЕНО: Добавлен верхний лимит (MAX_COPIES_LIMIT) на количество копий
    try:
        copies_int = int(job.copies)
        if copies_int <= 0:
            return False, f"Copies count must be > 0, got: {copies_int}"
        if copies_int > MAX_COPIES_LIMIT:
            return False, (
                f"Copies count exceeds maximum safety limit ({MAX_COPIES_LIMIT}), "
                f"got: {copies_int}"
            )
    except ValueError:
        return False, f"Invalid non-integer COPIES value: '{job.copies}'"

    if not job.user_name or job.user_name.strip() == "":
        return False, "USER_NAME cannot be empty"

    # Обратите внимание: проверка существования файла перенесена из соображений TOCTOU
    # непосредственно в момент открытия дескрипторов перед запуском бэкенда.
    return True, ""


def send_job_metadata(job: JobInfo) -> tuple[str, str]:
    """
    Sends metadata to Java API. Returns (ACTION, REASON) with Configurable Policy.
    """
    if not ENABLE_API:
        logger.info(f"[MOCK] API disabled. Job {job.job_id} automatically ALLOWED.")
        return "ALLOW", ""
