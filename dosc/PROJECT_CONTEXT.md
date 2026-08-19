# PROJECT_CONTEXT.md

# Print Management Core

## AI / Developer Project Context

**Project:** Print Management Core
**Short name:** PMC
**Current architecture generation:** 4.0
**Document purpose:** Bootstrap context for developers and AI assistants
**Current state:** Product discovery / architecture redesign
**Previous generation:** 3.x infrastructure-oriented implementation

---

# 1. READ THIS FIRST

This document is the primary bootstrap context for development work on Print Management Core.

A new developer or AI assistant should read this document before proposing:

* architecture;
* code;
* database schemas;
* deployment;
* infrastructure;
* APIs;
* implementation plans.

Do not assume that the previous 3.x implementation is the current architecture.

PMC 4.0 is a deliberate architectural reset.

The project has moved from:

> infrastructure-first HA system

to:

> product-first portable print-management platform.

The previous implementation contains useful experiments and reusable components, but it must not automatically define the new architecture.

---

# 2. PRODUCT IN ONE SENTENCE

> Print Management Core is a simple, portable and repairable platform for managing the lifecycle of corporate print jobs on top of CUPS.

---

# 3. PRODUCT IDEA

The central idea of PMC is:

> **Print Job Lifecycle Management**

The product is built around the lifecycle of a print job.

The system must allow an administrator to understand and control what happens to a print job from submission until completion, cancellation or failure.

The central entity is therefore:

**Print Job**

not:

* Docker;
* PostgreSQL;
* Java;
* Python;
* Keepalived;
* a particular server;
* a particular deployment model.

---

# 4. PROBLEM WE ARE SOLVING

CUPS is an excellent system print subsystem, but it does not by itself provide the complete operational view required by an organization.

PMC should answer questions such as:

* Who printed?
* What was printed?
* When?
* Where?
* Which queue?
* Which printer?
* What state is the job in?
* How long has it been waiting?
* Why did it fail?
* Was it retried?
* Was it cancelled?
* Who cancelled it?
* Which printer is producing errors?
* How many jobs failed?
* How much does each user print?
* Which printers are overloaded?
* What happened before an incident?

---

# 5. PRODUCT PRINCIPLES

## 5.1 Product First

The product determines infrastructure requirements.

Not the other way around.

---

## 5.2 CUPS First

PMC must use and extend CUPS rather than replace it.

CUPS remains responsible for native Linux printing.

PMC provides management and intelligence around it.

---

## 5.3 Simplicity

Prefer the simplest architecture that satisfies requirements.

Avoid:

* unnecessary microservices;
* unnecessary distributed systems;
* unnecessary clustering;
* unnecessary queues;
* unnecessary infrastructure dependencies.

---

## 5.4 Repairability

Every subsystem must be understandable and diagnosable.

A future administrator should be able to maintain the system without contacting the original author.

---

## 5.5 Portability

The product must not depend on a particular physical server.

Supported environments should include:

* physical Linux;
* virtual machines;
* Docker;
* future HA environments.

---

## 5.6 Observability

Important state changes must be observable.

Logs and audit data should explain:

* what;
* when;
* where;
* why;
* result.

---

## 5.7 Backup / Restore

Backup and restore are product features.

The desired recovery workflow is:

```text
New Linux server
        ↓
Install PMC
        ↓
Restore backup
        ↓
PMC operational
```

Manual reconstruction of the entire system should not be required.

---

# 6. TARGET USERS

Primary target:

**SMB organizations**

Typical scale:

* 10–500 users;
* several to dozens of printers.

Possible future scale:

* larger organizations;
* multiple sites;
* enterprise integrations.

The architecture must not be unnecessarily optimized for enterprise scale before the SMB use case is solved properly.

---

# 7. USER ROLES

## Print Administrator

Needs:

* queues;
* jobs;
* printer states;
* errors;
* job lifecycle;
* history;
* statistics.

---

## System Administrator

Needs:

* installation;
* configuration;
* upgrades;
* backup;
* restore;
* diagnostics;
* integration.

---

## Management / Reporting

Needs:

* statistics;
* reports;
* user activity;
* printer utilization;
* error rates.

---

# 8. CORE MVP

The first usable product should focus on:

## Print Jobs

* list;
* search;
* filtering;
* status;
* history;
* cancel;
* retry / reprint;
* pause;
* resume where supported;
* lifecycle tracking.

---

## Queues

* list;
* status;
* pending jobs;
* pause;
* resume;
* administration.

---

## Printers

* status;
* availability;
* errors;
* history;
* activity;
* statistics.

---

## Users

Initial version:

**Manual identity database.**

Future:

* LDAP;
* Active Directory;
* other identity providers.

---

## Monitoring

Track:

* job failures;
* printer errors;
* queue problems;
* service problems;
* important system events.

---

## Statistics

At minimum:

* jobs per user;
* pages per user when reliably available;
* jobs per printer;
* pages per printer;
* errors;
* failures;
* time-based activity.

---

## Administration

* Web UI;
* CLI;
* REST API;
* backup;
* restore;
* diagnostics;
* health check.

---

# 9. INTENTIONALLY DEFERRED

The following are NOT MVP requirements:

* quotas;
* billing;
* print cost accounting;
* advanced print policies;
* LDAP;
* Active Directory;
* secure print;
* follow-me printing;
* distributed spool;
* HA;
* multi-site replication.

They may be introduced later.

Do not add them to the core architecture prematurely.

---

# 10. IMPORTANT ARCHITECTURAL DECISION

PMC does not replace CUPS.

Conceptually:

```text
User / Client
      ↓
     CUPS
      ↓
PMC integration / Print Agent
      ↓
PMC Core
      ↓
Print Job Lifecycle
      ↓
Statistics / Audit / Monitoring
```

The exact implementation of this relationship is NOT yet frozen.

Do not assume that the existing Python backend is the final implementation.

---

# 11. PRINT JOB IS THE CORE ENTITY

The product should revolve around a print job.

Conceptual model:

```text
User
  ↓
Print Job
  ├── Queue
  ├── Printer
  ├── Events
  ├── State transitions
  ├── Errors
  ├── Audit
  └── Statistics
```

The exact domain model is still under design.

---

# 12. PRINT JOB LIFECYCLE

The lifecycle must eventually model states such as:

```text
SUBMITTED
    ↓
RECEIVED
    ↓
QUEUED
    ↓
PROCESSING
    ↓
PRINTING
    ↓
COMPLETED
```

Alternative paths:

```text
QUEUED
   ↓
PAUSED
   ↓
QUEUED
```

```text
QUEUED
   ↓
CANCELLED
```

```text
PRINTING
   ↓
FAILED
```

```text
FAILED
   ↓
RETRY
   ↓
QUEUED
```

This is conceptual only.

The definitive state machine must be designed and approved before implementation.

---

# 13. IDENTITY

The current historical project used static IP mapping.

CUPS can provide job metadata such as:

* job ID;
* user;
* host;
* queue;
* job title;
* options;
* submission time;
* size;
* state;
* completion information.

However:

> IP address and hostname alone must NOT automatically be treated as a reliable human identity.

They can be used as identity signals and fallback mechanisms.

Future identity integration:

```text
Manual
   ↓
LDAP
   ↓
Active Directory
   ↓
Other Identity Providers
```

Identity architecture must remain replaceable.

---

# 14. PYTHON ROLE

The previous project used a Python CUPS backend.

Its current role should NOT automatically be considered final.

The previous Python component was designed primarily as a print backend / wrapper.

It included security hardening and transport logic, but it was later determined that it did not provide enough functionality for the intended product.

The new architecture must first define the required Print Job lifecycle and CUPS integration model.

Only then should the final Python role be determined.

Possible role:

**PMC Print Agent**

rather than merely:

**Python wrapper**

The agent may eventually:

* observe CUPS;
* collect metadata;
* report job events;
* communicate with PMC Core;
* coordinate lifecycle events.

Exact responsibilities are still to be designed.

---

# 15. JAVA

The previous 3.x implementation introduced a Java/Spring Boot service.

It implemented functionality including:

* REST API;
* job processing;
* retry logic;
* PostgreSQL integration;
* audit persistence;
* quota-related logic.

This implementation is considered **legacy/prototype architecture for 4.0**.

Do not assume that Java must remain the core application language.

The new product architecture must decide the implementation stack based on product requirements.

---

# 16. DATABASE

The previous architecture used PostgreSQL.

PostgreSQL remains a possible database technology.

However:

> The database choice for PMC 4.0 is not yet frozen.

The first architectural question is the domain model and required persistence semantics.

Do not design the domain around PostgreSQL-specific features unless explicitly approved.

---

# 17. WEB UI

A Web UI is a core MVP requirement.

The primary UI should allow an administrator to see:

### Dashboard

* system health;
* printers;
* queues;
* active jobs;
* failed jobs;
* recent events.

### Jobs

* all jobs;
* filters;
* search;
* lifecycle;
* actions.

### Printers

* status;
* queues;
* errors;
* history;
* statistics.

### Users

* identity;
* activity;
* print statistics.

### Reports

* usage;
* failures;
* printer reliability;
* user activity.

The exact UI technology is not yet frozen.

---

# 18. CLI

The product should provide a CLI for administration and diagnostics.

Possible future commands:

```text
pmc status
pmc jobs
pmc printers
pmc users
pmc backup
pmc restore
pmc diagnostics
```

Exact command syntax is not yet approved.

---

# 19. REST API

A REST API is expected to provide programmatic access to the core.

Potential areas:

```text
/api/v1/jobs
/api/v1/printers
/api/v1/queues
/api/v1/users
/api/v1/events
/api/v1/reports
/api/v1/system
```

These paths are examples, not frozen API contracts.

Do not implement them until the domain model is approved.

---

# 20. DEPLOYMENT PHILOSOPHY

The product must support simple deployment.

Preferred conceptual workflow:

```text
Clean Linux
    ↓
One installation command
    ↓
PMC installed
    ↓
CUPS detected
    ↓
Configuration initialized
    ↓
Database initialized
    ↓
Web UI available
```

Docker is optional.

Docker must not become a prerequisite for basic operation.

---

# 21. DOCKER

Docker is considered:

**Deployment technology**

not:

**Application architecture**

The application must not depend on Docker-specific semantics.

A Docker deployment should package the same logical components used by native deployment.

---

# 22. HIGH AVAILABILITY

HA is NOT part of the MVP.

The previous project spent significant effort on:

* two physical nodes;
* Keepalived;
* VIP;
* Active-Passive architecture;
* PostgreSQL DR;
* failover;
* UPS coordination.

This was valuable infrastructure experimentation.

However, PMC 4.0 deliberately moves HA to a future infrastructure profile.

Conceptually:

```text
PMC Core
   │
   ├── Single Server
   ├── VM
   ├── Docker
   └── Future HA Profile
```

The core application must not require HA.

---

# 23. LEGACY 3.x INFRASTRUCTURE

The previous project was:

**PrintManagement_ProductionReady_SMB_HA**

Architecture:

**Hybrid Host + Docker Active-Passive Monolith**

Two nodes:

```text
print-node-1
print-node-2
```

Historical network:

```text
VIP: 10.1.10.230
node-1: 10.1.10.231
node-2: 10.1.10.232
```

Historical infrastructure:

* Ubuntu Server 24.04 LTS;
* mdadm RAID1;
* CUPS on host;
* PostgreSQL in Docker;
* Java in Docker;
* Python CUPS backend;
* Keepalived;
* Netdata;
* apcupsd;
* monitoring scripts;
* Telegram / Email notifications.

This architecture is retained as historical knowledge and as a source of reusable implementation ideas.

It is NOT automatically the PMC 4.0 architecture.

---

# 24. COMPLETED LEGACY STAGES

The following stages were completed in the 3.x implementation.

## S1.1 BIOS / Hardware Baseline

Completed.

Validated:

* CPU;
* RAM;
* SSD;
* HDD;
* UPS;
* cooling;
* SMART;
* basic BIOS configuration.

Known limitation:

* Non-ECC memory.

---

## S1.2 Ubuntu Base Installation

Completed.

Ubuntu:

**24.04 LTS Minimal**

Historical hostnames:

* print-node-1;
* print-node-2.

SSH, DNS, NTP and reboot persistence were validated.

---

## S1.3 RAID / Filesystem

Completed.

RAID1:

```text
/dev/md0
```

Filesystem:

```text
ext4
```

Historical storage:

```text
/srv/backups
/srv/archive
/srv/snapshots
/var/spool/cups
```

RAID degradation and rebuild were tested.

Important historical finding:

Node storage sizes differed:

* node-1 ≈ 1 TB;
* node-2 ≈ 500 GB.

This is relevant only if the old HA architecture is reused.

---

## S1.4 Base Security

Completed.

Implemented:

* SSH key authentication;
* password authentication disabled;
* root login disabled;
* sudo;
* UFW;
* fail2ban;
* persistent journald;
* reboot validation.

Historical management user:

```text
srvadmin
```

---

## S1.5 Monitoring Foundation

Completed.

Monitoring framework was adapted from NASNF.

Channels:

* Telegram;
* Email.

Historical secret location:

```text
/etc/print-monitor/secrets.conf
```

Permissions:

```text
600
```

State directory:

```text
/var/lib/print-monitor/state/
```

Log:

```text
/var/log/print-monitor/alerts.log
```

Monitors included:

* disk;
* RAID;
* SMART;
* system;
* temperature;
* daily health report.

Systemd timers were used.

---

# 25. DOCKER LEGACY STAGE

Docker was installed and validated.

Historical versions:

* Docker 29.6.1;
* Compose v5.2.0.

Persistent storage root:

```text
/srv/docker
```

Historical directories:

```text
/srv/docker/postgresql
/srv/docker/nginx
/srv/docker/java
/srv/docker/python
/srv/docker/logs
/srv/docker/volumes
```

Owner:

```text
srvadmin:docker
```

Mode:

```text
750
```

---

# 26. POSTGRESQL LEGACY STAGE

Historical PostgreSQL:

```text
PostgreSQL 16.14
```

Container:

```text
postgres_print_db
```

Historical data:

```text
/srv/docker/postgresql/data
```

CPU limit:

```text
1 core
```

RAM limit:

```text
2048 MiB
```

The persistence model survived container destruction.

---

# 27. CUPS LEGACY STAGE

CUPS was deliberately placed on the host.

Reason:

* native Linux print stack;
* direct CUPS integration;
* predictable queue behavior;
* simpler printer handling.

Historical CUPS:

```text
CUPS 2.4
```

Spool:

```text
/var/spool/cups
```

Spool was located on RAID1.

CUPS was bound locally:

```text
127.0.0.1:631
[::1]:631
```

Remote administration and printer sharing were disabled.

This architectural decision remains highly relevant to PMC 4.0.

---

# 28. PYTHON BACKEND LEGACY

Historical path:

```text
/usr/lib/cups/backend/print-wrapper
```

Language:

```text
Python 3
```

Dependencies:

**stdlib only**

Security work included:

* strict URI scheme validation;
* path traversal protection;
* TOCTOU mitigation;
* copy limits;
* robust CUPS option parsing;
* subprocess descriptor handling;
* API fail-safe strategy;
* database decoupling;
* stderr logging.

However, this implementation was later considered insufficient for the broader product goals.

Important:

> Do not automatically reuse it as the final PMC 4.0 Print Agent.

Use it as a technical reference only.

---

# 29. JAVA LEGACY IMPLEMENTATION

Historical Java service:

```text
print-java-api
```

Technology:

* Spring Boot 3;
* Java 17;
* Hibernate/JPA.

Historical features:

* POST /api/print;
* health endpoint;
* async processing;
* retry engine;
* PostgreSQL persistence;
* audit;
* quota logic;
* structured communication with Python.

It was deployed in Docker.

This architecture is considered legacy for PMC 4.0.

Do not assume Java remains mandatory.

---

# 30. WHY THE ARCHITECTURE WAS RESET

During implementation it became clear that the infrastructure had started driving the product.

The system had accumulated:

* HA;
* multiple nodes;
* Keepalived;
* PostgreSQL DR;
* Docker;
* Java;
* Python;
* monitoring;
* UPS logic.

At the same time, the actual product requirements were broader:

* queue management;
* job lifecycle;
* cancellation;
* pause;
* retry;
* statistics;
* printer reliability;
* user activity;
* error analysis.

The conclusion was:

> The product should be designed first. Infrastructure should follow.

Therefore PMC 4.0 is a deliberate redesign rather than a continuation of the old implementation.

---

# 31. WHAT IS REUSABLE FROM 3.x

Potentially reusable:

* CUPS host deployment decision;
* monitoring concepts;
* notification framework;
* security practices;
* backup philosophy;
* installation automation;
* Python security hardening;
* operational experience;
* testing methodology;
* Linux deployment knowledge.

Not automatically reusable:

* HA topology;
* Keepalived configuration;
* two-node assumptions;
* Java architecture;
* Docker-dependent architecture;
* old database schema;
* old API;
* old Print Job model.

Everything must be reviewed against PMC 4.0 requirements.

---

# 32. CURRENT DEVELOPMENT STATE

## Product Vision

Status:

**Draft / being formalized**

---

## Product Scope

Status:

**Being defined**

---

## Product Requirements

Status:

**Not yet frozen**

---

## Domain Model

Status:

**Not yet frozen**

---

## Print Job Lifecycle

Status:

**Conceptual only**

This is the next major design task.

---

## Application Architecture

Status:

**Not frozen**

---

## Database Model

Status:

**Not frozen**

---

## API

Status:

**Not frozen**

---

## UI

Status:

**Not frozen**

---

## Deployment

Status:

**Conceptual**

---

## Implementation

PMC 4.0 implementation has NOT formally started.

The previous 3.x implementation should be treated as legacy/reference material.

---

# 33. CURRENT ROADMAP

```text
A0 Product Discovery
        ↓
A1 Product Vision
        ↓
A2 Product Scope
        ↓
A3 Product Requirements
        ↓
A4 MVP Definition
        ↓
A5 Domain Model
        ↓
A6 Print Job Lifecycle
        ↓
A7 Application Architecture
        ↓
A8 Deployment Architecture
        ↓
A9 Implementation
        ↓
A10 Testing
        ↓
A11 Release
```

The exact numbering may be adjusted as the architecture develops.

---

# 34. NEXT IMMEDIATE TASK

The next major task is:

**Design the Print Job Lifecycle.**

Before implementing:

* Python Agent;
* Java;
* REST API;
* database;
* Web UI;

we must define the behavior of a print job.

We need to determine:

* states;
* transitions;
* events;
* failure states;
* retry behavior;
* cancellation;
* pause;
* resume;
* reprint;
* ownership;
* timestamps;
* error information;
* relationship with CUPS.

---

# 35. DESIGN RULE FOR THE NEXT STAGE

Do NOT start implementation from technology.

Do NOT start with:

> "Let's create the Java service."

Do NOT start with:

> "Let's create the PostgreSQL schema."

Do NOT start with:

> "Let's rewrite the Python backend."

First define:

> What happens to one print job?

Then derive the architecture from that behavior.

---

# 36. DEVELOPMENT WORKFLOW

The project uses separate implementation chats.

Master context:

```text
PROJECT_CONTEXT.md
```

Architecture decisions:

```text
ADR/
```

Implementation chats:

```text
Implementation/
```

Each implementation chat should:

1. receive the relevant project context;
2. have a narrowly defined task;
3. make changes only within that scope;
4. test the result;
5. report exactly what was changed;
6. report problems;
7. report remaining risks;
8. return a structured completion summary.

---

# 37. IMPLEMENTATION CHAT RULES

An implementation chat must NOT redesign the entire product.

If it discovers an architectural problem:

1. stop;
2. describe the problem;
3. propose alternatives;
4. return the issue to the architecture/master context.

Do not silently change architectural decisions.

---

# 38. TESTING PRINCIPLE

Every implementation step must be independently verifiable.

Preferred workflow:

```text
Implement
   ↓
Test
   ↓
Verify
   ↓
Document
   ↓
Commit
   ↓
Next step
```

Never build several unverified layers simultaneously.

---

# 39. ARCHITECTURE DECISION RULE

When a significant decision is made:

```text
Discussion
    ↓
Decision
    ↓
ADR
    ↓
Implementation
```

Important decisions must not exist only inside chat history.

---

# 40. AI ASSISTANT INSTRUCTIONS

When starting a new development chat:

### First

Read `PROJECT_CONTEXT.md`.

### Then

Identify:

* current architecture;
* current stage;
* relevant requirements;
* legacy components;
* known constraints.

### Before proposing implementation

Check whether the requested functionality is:

* MVP;
* planned;
* deferred;
* rejected;
* not yet defined.

### Never

Assume old 3.x architecture is current.

### Never

Introduce infrastructure complexity without a product requirement.

### Never

Choose a technology before understanding the required behavior.

### Always

Prefer:

* simple;
* explicit;
* observable;
* testable;
* repairable;
* portable.

---

# 41. QUESTIONS TO ASK BEFORE IMPLEMENTATION

For every significant component:

1. What problem does it solve?
2. Is the problem part of MVP?
3. Can CUPS already solve it?
4. Can PMC extend CUPS instead of replacing it?
5. Is the component necessary?
6. Can the component be simpler?
7. Can it run without Docker?
8. Can it be tested independently?
9. Can another administrator diagnose it?
10. Can it be restored from backup?

---

# 42. CURRENT HARD CONSTRAINTS

The following principles are currently considered strong constraints:

* Linux-first;
* CUPS-first;
* simple deployment;
* Docker optional;
* repairability;
* observability;
* backup/restore;
* product-first architecture;
* print-job-centric domain;
* no premature HA;
* no unnecessary distributed systems.

---

# 43. CURRENT OPEN QUESTIONS

These questions must be answered before implementation:

* Exact Print Job state machine?
* Exact role of Python Print Agent?
* Should the core application use Java, Python, another language, or a combination?
* PostgreSQL or another persistence layer?
* How exactly should CUPS events be captured?
* How reliably can user identity be determined?
* How should reprint work when the original print data is unavailable?
* Should PMC retain print data or only metadata?
* How should pause/resume map to CUPS?
* How should printer errors be normalized?
* What constitutes a failed job?
* How should retries be represented?
* What data is required for reliable statistics?
* What is the minimum installation footprint?
* What backup format should be used?
* How should upgrades and migrations work?

These are design questions, not implementation bugs.

---

# 44. SECURITY PRINCIPLES

The final architecture must include:

* least privilege;
* no unnecessary root execution;
* secure secrets;
* explicit authentication;
* authorization;
* audit logging;
* safe handling of print metadata;
* input validation;
* controlled subprocess execution;
* secure backup handling.

Exact security architecture is not yet frozen.

---

# 45. OPERATIONAL PRINCIPLES

The system should provide:

* clear logs;
* health checks;
* diagnostics;
* predictable startup;
* predictable shutdown;
* recoverable failures;
* configuration validation;
* backup verification;
* restore verification.

The administrator should never need to guess whether the system is healthy.

---

# 46. PROJECT PHILOSOPHY

The most important principle:

> **Do not build infrastructure because it is technically interesting. Build it only when the product requires it.**

Second:

> **Do not implement features because they sound useful. Implement them because they solve a defined user problem.**

Third:

> **Do not optimize for theoretical scale before solving the real operational problem.**

Fourth:

> **Prefer a boring solution that works over an impressive solution that is difficult to maintain.**

---

# 47. FINAL CONTEXT FOR NEW DEVELOPERS

If you remember only ten things about PMC, remember these:

1. PMC is a print-management product, not an HA infrastructure project.
2. CUPS remains the native print engine.
3. Print Job is the central domain entity.
4. Job lifecycle is the heart of the product.
5. Docker is optional.
6. HA is future infrastructure, not MVP.
7. Quotas are deferred.
8. The previous 3.x implementation is legacy/reference material.
9. Product behavior must be designed before implementation technology.
10. Simplicity and repairability are architectural requirements, not aesthetic preferences.

---

# 48. CURRENT NEXT ACTION

The next design document should define:

**Print Job Lifecycle**

It must specify:

* states;
* transitions;
* events;
* cancellation;
* pause;
* resume;
* retry;
* reprint;
* failures;
* CUPS interaction;
* audit events;
* timestamps;
* ownership;
* statistics implications.

Only after this document is approved should the implementation architecture be designed.

---

# END OF PROJECT CONTEXT
