---
title: Directory Structure
---
The thing with using a tool is to get the grasp of the bigger picture. I like to know how the environment of the tool that I use usually looks like in dev / prod. I'm not well versed with how an actual backend directory structure should look like, but let's start with something very simple. There seems to be two recommended ways: one for small to medium sized apps, and another for large apps. Let's write down both to consider when making or working on projects.

To be honest, I don't think I will be ever using the second type of structure, so just rely on the first structure.

> [!tip]
> **Best Practices**
> - **Keep `main.py` Thin:** Avoid putting route logic. Use it only to instantiate your app, configure CORS middleware, handle startup/shutdown lifespans, and attach routers via `app.include_router()`.
> - **Decouple Models and Schemas:** Always keep database ORM files (`models/`) distinct from Pydantic contract files (`schemas/`). Mixing them results in tight coupling, circular import loops, and data validation bottlenecks.
> - **Isolate Configuration:** Use `pydandic-settings` inside `core/config.py` to pull variables from your environment or `.env` files dynamically, allowing your code to remain secure and transportable.

## Structure 1: Organized by Layer (Best for Medium Apps)

This approach is popular for small-to-medium APIs. It separates your application logic by architectural responsibility (routes, business logic, and database). 

```text
my_fastapi_project/
├── alembic/                  # Database migration files (if using Alembic)
├── app/                      # Main application package
│   ├── api/                  # API layer (HTTP routers and endpoints)
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   └── deps.py           # Common FastAPI dependencies (e.g., get_db, get_current_user)
│   ├── core/                 # Application configuration & security setup
│   │   ├── config.py         # Pydantic Settings for environment variables
│   │   └── security.py       # Password hashing and JWT generation
│   ├── crud/                 # Raw database interactions (Create, Read, Update, Delete)
│   │   ├── crud_user.py
│   │   └── crud_item.py
│   ├── db/                   # Database setup
│   │   ├── base.py           # Base model class for SQLAlchemy/SQLModel
│   │   └── session.py        # Database engine and sessionmaker config
│   ├── models/               # Database ORM models (SQLAlchemy, SQLModel, Tortoise, etc.)
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/              # Pydantic data schemas (Request validation & Response serialization)
│   │   ├── user.py
│   │   └── item.py
│   ├── services/             # Business logic layer (Glue code between routes and data access)
│   │   └── payment.py
│   ├── __init__.py
│   └── main.py               # Application entrypoint (Initializes FastAPI and registers routers)
├── tests/                    # Test suite (using pytest)
│   ├── conftest.py          # Pytest shared fixtures
│   ├── api/                  # API integration tests
│   └── services/             # Unit tests for business logic
├── .env                      # Local secret environment variables
├── .gitignore
├── .python-version           # Pins Python version for uv
├── README.md
├── pyproject.toml            # Project metadata & dependencies (uv-managed)
└── uv.lock                   # Locked, reproducible dependency versions
```

## Structure 2: Organized by Domain/Feature (Best for Large Apps)

If you are building a larger monolith, organizing by file type quickly becomes cluttered. Instead, keep everything related to a specific feature inside one self-contained domain folder.

```text
my_fastapi_project/
├── app/
│   ├── core/                 # Shared configs, middleware, and core security
│   │   ├── config.py
│   │   └── database.py
│   ├── users/                # All code related to users
│   │   ├── router.py         # User endpoints
│   │   ├── models.py         # User DB model
│   │   ├── schemas.py        # User Pydantic data shapes
│   │   ├── service.py        # User business rules
│   │   └── dependencies.py   # User-specific route dependencies
│   ├── products/             # All code related to products
│   │   ├── router.py
│   │   ├── models.py
│   │   └── ...
│   └── main.py
└── ...
```

***

[Last modified: 2026-07-09]{.note-modified}
