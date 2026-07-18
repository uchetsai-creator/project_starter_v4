# Permissions

<!--
  Describes roles, permission definitions, and access control rules for this project.

  Which project types need this file:
    Web App / Microservices — full RBAC / ABAC / ACL model; document every endpoint
    CLI Tool                — document which commands require elevated privileges or config
    AI / LLM App            — document who can invoke the app and any output restrictions
    Data Pipeline           — document who can trigger runs and access output data
    Library / SDK           — usually no permissions (caller controls access); skip if so

  Access control model: fill in the actual model used in this project.
  Common models:
    RBAC       — Role-Based Access Control (roles → permissions → endpoints)
    ABAC       — Attribute-Based Access Control (user/resource attributes drive rules)
    ACL        — Access Control List (per-resource entries)
    API Key    — key-based access, no user roles (common for libraries and LLM apps)
    Ownership  — no roles; each user can only access their own resources

  The sections below assume RBAC / HTTP API. Replace or skip sections that don't apply.
  After writing: edit the ```plantuml block in the file, then rebuild PDF
-->

**Access Control Model:** [RBAC / ABAC / ACL / Ownership-only / other]

---

## Role Definitions

<!--
  List the actual roles in this project.
  The three roles below (GUEST / USER / ADMIN) are examples — replace with real role names.
  Inherits from is optional — omit the column if roles do not inherit from each other.
-->

| Role | Description | Inherits from |
|---|---|---|
| `[ROLE_NAME]` | [Who this role represents and what they can access] | [— or parent role] |
| `[ROLE_NAME]` | [Description] | [— or parent role] |

---

## Permission Definitions

| Permission | Description |
|---|---|
| `[resource]:read` | Read [resource] |
| `[resource]:create` | Create [resource] |
| `[resource]:update` | Update own [resource] |
| `[resource]:update:any` | Update any [resource] |
| `[resource]:delete` | Delete own [resource] |
| `[resource]:delete:any` | Delete any [resource] |

---

## RBAC Matrix

<!--
  ✅ Allowed
  ❌ Denied
  🔶 Conditionally allowed (see notes below)
-->

| Permission | ROLE_GUEST | ROLE_USER | ROLE_ADMIN |
|---|---|---|---|
| `[resource]:read` | ✅ | ✅ | ✅ |
| `[resource]:create` | ❌ | ✅ | ✅ |
| `[resource]:update` | ❌ | 🔶 | ✅ |
| `[resource]:update:any` | ❌ | ❌ | ✅ |
| `[resource]:delete` | ❌ | 🔶 | ✅ |
| `[resource]:delete:any` | ❌ | ❌ | ✅ |

**🔶 Conditions:**
* `[resource]:update` — `ROLE_USER` may only update resources where `owner_id = current_user.id`
* `[resource]:delete` — `ROLE_USER` may only delete resources where `owner_id = current_user.id`

---

## API Endpoint Access

<!--
  Cross-check required before finalising this table:
  For every role listed as a "Responsible role" or "Owner" in any docs/business/*-process.md,
  verify that role has at least the minimum endpoint access needed to perform its responsibility.

  A role that is assigned a business responsibility but denied the required endpoint
  is a logical contradiction — it must be resolved here, not left to the implementer to guess.

  Steps:
  1. Read every *-process.md file
  2. Note every (role, action) pair in the Process Steps and Responsible role columns
  3. Confirm each role can reach the endpoint that supports that action
  4. If a gap exists, either grant access or explicitly document why the role uses
     a different path (e.g., via a supervisor, via a separate tool)

  Source column — mandatory distinction:
  Every row must specify whether access is a Hardcoded constraint or a Seeded default:
    - Hardcoded: enforced in code (middleware with a fixed role list, route guard with
      roles=[...]). Cannot be changed without a deployment. Document as a definitive rule
      in business-rules.md if it encodes a business policy.
    - Seeded default: the starting state in the database/role table. Can be changed at
      runtime by an admin (e.g. via a Role Management page). Document as "(Default)" —
      do NOT write it as a permanent rule in business-rules.md, since it can change
      without a code deploy.

  If this project has a Role Management feature, most role-permission rows are seeded
  defaults, not hardcoded constraints. Mixing them up causes contradictions between
  business-process.md (what a role should be able to do) and this table (what the role
  can access right now, which may just be today's default).
-->

| Method | Path | Required permission | Minimum role | Source | Extra condition |
|---|---|---|---|---|---|
| `POST` | `/[resource]` | `[resource]:create` | `ROLE_USER` | [Hardcoded / Seeded default] | — |
| `GET` | `/[resource]` | `[resource]:read` | `ROLE_GUEST` | [Hardcoded / Seeded default] | — |
| `GET` | `/[resource]/:id` | `[resource]:read` | `ROLE_GUEST` | [Hardcoded / Seeded default] | — |
| `PATCH` | `/[resource]/:id` | `[resource]:update` | `ROLE_USER` | [Hardcoded / Seeded default] | Own resource only |
| `DELETE` | `/[resource]/:id` | `[resource]:delete` | `ROLE_USER` | [Hardcoded / Seeded default] | Own resource only |

---

## Enforcement Layers

<!--
  Describe where access control is enforced.
  Use the rows that match your project type — remove inapplicable rows.
-->

| Layer | Responsibility | Applies to |
|---|---|---|
| API Gateway | Token validation, role extraction | Web App / Microservices |
| Middleware / Route Guard | Role-permission check, reject unauthorized | Web App / Microservices |
| Service Layer | Ownership check — `owner_id = current_user.id` | Web App |
| CLI Flag / Config | Require elevated flag or config key for privileged commands | CLI Tool |
| API Key Header | Validate key before processing any request | AI/LLM App / Library |
| Pipeline Trigger Auth | Verify caller identity before allowing pipeline run | Data Pipeline |

---

## Edge Cases

<!--
  List access control edge cases relevant to your project type.
  Remove HTTP-specific rows if your project is not a Web App / Microservices.
-->

| Edge Case | Design | Response |
|---|---|---|
| Unauthenticated access to protected resource | Token / key check at entry point fails | Reject with auth error (HTTP 401 / non-zero exit / exception) |
| Low-privilege role attempts high-privilege action | Role-permission check | Reject (HTTP 403 / permission denied error) |
| User accesses another user's resource | Ownership check in service layer | Reject (HTTP 403 / access denied) |
| Expired / revoked token or API key | Token validation fails | Reject with auth error |
| Privileged CLI command run without required flag | Arg parser check | Exit with usage error |
| Pipeline triggered by unauthorized caller | Trigger auth check | Reject run request |

---

## Use Case Diagram

<!--
  System-level view — list ALL roles and ALL major functions across all modules.
  Not per resource, not per module — the whole system in one diagram.
  After writing, run: Edit the ```plantuml block in the file, then rebuild PDF
-->

```plantuml
@startuml
' ── UML Use Case Diagram Rules ──────────────────────────────────────────────
' ACTORS: use inheritance — only draw lines unique to each actor level
' USE CASES: verb-oriented user goals, NOT UI pages or domain objects
'   ❌ "Dashboard"  ✔ "Monitor production status"
'   ❌ "Equipment"  ✔ "View equipment status"
' UC RELATIONSHIPS: <<include>> (always) or <<extend>> (conditionally)
'   ❌ UC1 --> UC2   ✔ UC1 ..> UC2 : <<include>>

left to right direction
skinparam packageStyle rectangle

actor Operator
actor Supervisor
actor Admin

Supervisor --|> Operator
Admin      --|> Supervisor

rectangle "[System Name]" {
  usecase "Monitor [core function]"   as UC1
  usecase "View [resource] details"   as UC2
  usecase "Generate [X] report"       as UC3
  usecase "Handle [domain event]"     as UC4
  usecase "Manage [resource]"         as UC5
  usecase "Configure system settings" as UC6
}

Operator   --> UC1
Operator   --> UC2
Supervisor --> UC3
Supervisor --> UC4
Admin      --> UC5
Admin      --> UC6

' UC3 ..> UC1 : <<include>>
@enduml
```
