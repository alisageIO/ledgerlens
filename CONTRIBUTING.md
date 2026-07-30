# Contributing to LedgerLens

Thanks for contributing. These conventions keep the codebase uniform, reviewable, and
consistent. They are mandatory and enforced in CI.

This is a solo, 5-week MVP build (see [docs/PRD.md](./docs/PRD.md) §4/§7), so "team"
conventions below exist to keep the codebase reviewable by others later, not because
there's a team enforcing them today — treat them as self-discipline, checked by CI
instead of a reviewer.

## Getting started

1. Read [README.md](./README.md) and get the app running locally (`make dev`).
2. Branch off `main` (see below) — there is no `dev`/`staging` environment in this
   project; [docs/TRD.md](./docs/TRD.md) §8 only ever deploys a single `main` branch.
3. Backend: `cd backend && uv sync`. Web: `cd web && pnpm install`.

## Branching & pull requests

- Base all feature branches on `main`. Name them `feat/<scope>`, `fix/<scope>`,
  `chore/<scope>`, etc.
- Open pull requests into `main`.
- Keep PRs focused. Fill in the description, link the ticket (see
  [docs/tickets-milestone-1.csv](./docs/tickets-milestone-1.csv) / TICKETS.md), and make
  sure CI is green.
- Merge is blocked on a failing CI check — this requires branch protection to be turned
  on in the GitHub repo settings requiring the CI workflow's jobs; the workflow alone
  doesn't enforce it.

## Commits

- [Conventional Commits](https://www.conventionalcommits.org/) are enforced in CI via
  `commitlint` (`.github/workflows/ci.yml`'s `lint-commits` job, config in
  `commitlint.config.js`) on every pull request. Format: `type(scope): subject` — e.g.
  `feat(auth): add JWT issuance on login`.
- Types: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`, `ci`, `perf`, `build`,
  `style`.
- Commit incrementally. Land substantial, self-contained units as you go (e.g. model,
  then service, then route, then tests) rather than one large commit.

## Coding standards

These are non-negotiable. A PR that violates them will be sent back.

### 1. `HttpStatus` — no hardcoded status codes

```python
# Bad
return {"statusCode": 200, "message": "Profile fetched"}

# Good
from fastapi import status

return {"statusCode": status.HTTP_200_OK, "message": SYS_MSG.OPERATION_SUCCESSFUL, "data": data}
```

### 2. System message constants — no free-text strings

Source of truth: `backend/constants/system_messages.py`. Add the constant there before
using it anywhere — routes, services, and exception handlers all import from it so
wording stays uniform.

```python
# Bad
raise NotFoundException("User not found")

# Good
from constants import system_messages as SYS_MSG

raise NotFoundException(SYS_MSG.NOT_FOUND)
```

The backend doesn't use import aliases (no `@domain`, `@config`, etc.) — imports are
absolute from the `backend/` project root (`from domain.exceptions import ...`,
`from config.env import settings`), matching the depth shown in existing modules.

### 3. No `Any` in the codebase

Zero explicit `Any` types in DTOs, services, routes, or utilities — enforced by ruff's
`ANN401` rule (`backend/pyproject.toml`). Use precise types, generics, or `object` /
`unknown`-style narrowing instead. The one documented exception is
`api/envelope.py` (see the per-file ignore and its comment) — it wraps arbitrary,
already-serialized JSON by design, which is the one honest boundary where "no `Any`"
can't hold.

(mypy's `disallow_any_explicit` was tried first and dropped — it fires on the
`class Foo(BaseModel)` line itself for *every* Pydantic model via the `pydantic.mypy`
plugin, unrelated to actual `Any` usage in our code, so it would flag every DTO/entity
rather than real violations. `ANN401` lints source text directly, the same way the
TS equivalent — `@typescript-eslint/no-explicit-any` — does on the web side.)

### 4. Strongly typed signatures

Annotate all parameters and return types explicitly; `mypy` runs in CI
(`disallow_untyped_defs = true`).

```python
async def find_by_email(self, email: str) -> User | None: ...
```

### 5. Check before you create

Before adding any file/module/class/enum/DTO, search for an existing one and reuse it.
Before adding a file to a module, read at least 3 existing files of the same type and
match their style.

### 6. Folder layout per module

Backend: each domain concept gets its own package under `backend/domain/<name>/`
(entities/repository/service), with API-facing shape (routes, request/response schemas,
OpenAPI doc decorators) under `backend/api/`. See `backend/domain/shared/` for the base
classes every module extends (`Base` for entities, `AbstractRepository` for DB access).

Web: route segments live under `web/app/`, matching the route table in
[docs/FRONTEND.md](./docs/FRONTEND.md) §1; shared client-side logic lives in `web/lib/`.

### 7. Configuration

Never read `os.environ` directly outside `backend/config/env.py`; consume config via
the `settings` object it exports. On the web side, never read `process.env` directly
outside `web/lib/env.ts`; consume config via the `env` object it exports — both are
validated at import time (Pydantic `Settings` / Zod respectively) and fail fast on a
missing or malformed value rather than surfacing as a runtime error somewhere else.

### 8. Database access — `AbstractRepository`

Services must never inject a raw SQLAlchemy `Session` directly. Every entity gets a
repository extending `AbstractRepository` (`backend/domain/shared/repository.py`), and
the session is injected into the repository, never the service. No raw SQL anywhere
except Alembic migrations.

```python
# backend/domain/accounts/repository.py
class AccountRepository(AbstractRepository[Account]):
    model = Account

    def find_by_user(self, user_id: UUID) -> list[Account]:
        return self.session.query(Account).filter_by(user_id=user_id).all()
```

### 9. Casing

Entities and columns are snake_case (SQLAlchemy models map directly onto Postgres
columns); everything else — especially API responses — is camelCase. The `Envelope`
model's `alias_generator=to_camel` handles the outer shape; per-endpoint response
schemas should do the same via the shared Pydantic config, not a one-off per DTO.

### 10. Response envelope

Every response goes through `EnvelopeRoute` (`backend/api/envelope.py`). Register it on
every `APIRouter` you create — `router = APIRouter(route_class=EnvelopeRoute)` — since
`app.router.route_class` alone only covers routes added directly on `app`, not routes
added via `include_router`.

```python
router = APIRouter(prefix="/accounts", route_class=EnvelopeRoute)


@router.get("/")
def list_accounts() -> list[AccountOut]:
    return accounts_service.list_for_user(user_id)
```

Return plain, typed data from the route function — `EnvelopeRoute` wraps it into
`{success, statusCode, message, data, meta}` automatically. Don't construct the
envelope by hand inside a route.

### 11. Error handling

Raise `HTTPException` or a domain exception from `domain/exceptions.py` — never
`raise Exception(...)`. `register_exception_handlers` (`backend/api/exceptions.py`)
catches everything and normalizes it into the standard error envelope; a bare
`Exception` still gets caught by the catch-all handler, but loses any specific status
code and is logged as an unhandled error.

```python
# Bad
raise Exception("User not found")

# Good
from domain.exceptions import NotFoundError

raise NotFoundError(SYS_MSG.NOT_FOUND)
```

Add a new failure mode to `domain/exceptions.py` and its status-code mapping in
`api/exceptions.py`'s `_DOMAIN_ERROR_STATUS` dict rather than reaching for a generic
`HTTPException` from inside a service — domain services shouldn't know about HTTP
status codes at all.

### 12. No domain-event bus, no Redis/queues

This codebase has neither, deliberately — see ADR-001
([docs/TRD.md](./docs/TRD.md) §4): no cache or queue layer at MVP scale. Categorisation
runs as an in-process background task after import commits
([docs/implementation-guide.md](./docs/implementation-guide.md) §4.2), not via an event
emitter. Don't introduce `EventEmitter`-style patterns or a Redis/Celery dependency
without revisiting that ADR first.

### 13. JSDoc / docstrings on exported service methods

One-line docstring on every exported service method; private helpers don't need one.

```python
def find_by_id(self, id: UUID) -> User:
    """Returns the user or raises NotFoundError."""
```

### 14. No inline "what" comments

Code is self-explanatory via naming. Only comment when there's a hidden constraint or
non-obvious invariant a reader couldn't infer from the code (a specific edge case,
a workaround, a reason a check runs in a particular order).

## Swagger / OpenAPI documentation

FastAPI generates the OpenAPI schema from route signatures and `response_model`
directly — there's no separate hand-written doc-decorator layer to keep in sync.
Rules:

- Every route gets a `summary` and, where the behavior isn't obvious from the response
  model alone, a `description` — reference a `SYS_MSG` constant in the description
  where one exists for that outcome, rather than a free-text string.
- Document every status code the endpoint can actually return via `responses={...}`.
- Keep docstrings/descriptions wrapped at a reasonable width.

## Testing

Every module ships unit tests for its service layer; every route gets at least one
integration test through the FastAPI `TestClient`.

- `make backend-test` — `pytest` for the API
- `make web-lint` — `eslint` + `tsc --noEmit` for the web app
- `make web-build` — production build (the web project doesn't have a separate test
  suite yet; this is the closest thing to one until epic-level UI work starts)

## Environment variables

- Backend: declared in `backend/config/env.py`'s `Settings` (Pydantic), read via the
  exported `settings` object. `backend/.env.example` documents every variable; copy it
  to `.env` for local (non-Docker) runs.
- Web: declared in `web/lib/env.ts`'s Zod schema, read via the exported `env` object.
  `web/.env.example` documents every variable; copy it to `.env.local` for local runs.
- No secrets (JWT signing key, DB credentials, LLM API key) are committed to the repo.

## Before you open a PR

- [ ] No explicit `Any`; `make backend-lint` passes (ruff + mypy).
- [ ] No hardcoded HTTP status codes — `fastapi.status` constants only.
- [ ] Messages sourced from `system_messages.py`; no inline strings.
- [ ] New entities/repositories/schemas in their correct module folder.
- [ ] No direct `os.environ` / `process.env`; config read from `config/env.py` /
      `lib/env.ts`.
- [ ] No raw SQL (except Alembic migrations); DB access via a repository, not a raw
      session in the service.
- [ ] Entities snake_case; responses camelCase.
- [ ] Every new `APIRouter` registers `route_class=EnvelopeRoute`.
- [ ] Errors thrown via `HTTPException` / a `domain.exceptions` subclass, never a bare
      `Exception`.
- [ ] Exported service methods have a one-line docstring; no inline "what" comments.
- [ ] Reused existing code where possible; matched the style of 3+ similar files.
- [ ] Unit/integration tests added; `make backend-test` and `make web-build` pass.
- [ ] Any new Alembic migration is additive only (no column/table drops, no
      type-narrowing renames) — see [docs/TRD.md](./docs/TRD.md) §8's rollback story.
