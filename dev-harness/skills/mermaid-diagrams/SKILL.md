---
name: mermaid-diagrams
description: Generates clean, syntax-valid Mermaid diagrams (architecture flowcharts, database ER schemas, request sequence diagrams) for Markdown docs. Use whenever writing or auditing diagrams in docs/PLAN.md, README.md or any .md file, or when the user asks for an architecture, schema, ERD, flow or sequence diagram, even if they don't say "Mermaid".
---

# Mermaid diagrams

Diagrams in Markdown must render in VS Code and GitHub on the first try. A single unquoted bracket or stray character turns the whole block into an error box, so follow the syntax rules below exactly. Put each diagram in a fenced ```` ```mermaid ```` block.

## Diagrams to include
1. **System architecture** (`flowchart TD`): UI, backend routes/services, and data layers.
2. **Database schema** (`erDiagram`): tables, column types, PK/FK keys. Include whenever a database is present.
3. **Request sequence** (`sequenceDiagram`): step-by-step lifecycle of the core feature.

Skip a diagram type that does not apply (e.g. no ER diagram without a database).

## Strict syntax rules
- Quote any flowchart node text containing spaces, slashes, brackets, parentheses or colons:
  - Good: `API["FastAPI (/api/tasks)"]`
  - Bad: `API[FastAPI (/api/tasks)]`
- Use short alphanumeric node ids (`API`, `DB`, `UI`); never use `end` as an id.
- In `sequenceDiagram` labels, avoid raw parentheses and quotes (rephrase in plain words). `;` and `#` also break labels; write them as `#59;` and `#35;`.
- Declare sequence participants up front with simple aliases: `participant B as Browser`.
- In `erDiagram`, column types are single words (`string`, `int`, `uuid`); mark keys with `PK`/`FK`; relationships use `||--o{` style with a quoted label.
- Keep each diagram scannable: at most 12–15 nodes. Split into several diagrams rather than cramming.
- When auditing, fix existing diagrams in place and keep their meaning unchanged.

## Examples

```mermaid
flowchart TD
    UI["React UI"] --> API["FastAPI (/api/tasks)"]
    API --> SVC["Task service"]
    SVC --> DB[("PostgreSQL")]
```

```mermaid
erDiagram
    USER ||--o{ TASK : "owns"
    USER {
        uuid id PK
        string email
    }
    TASK {
        uuid id PK
        uuid user_id FK
        string title
    }
```

```mermaid
sequenceDiagram
    participant B as Browser
    participant A as FastAPI
    participant D as Database
    B->>A: POST /api/tasks
    A->>D: INSERT task
    D-->>A: task row
    A-->>B: 201 Created
```
