from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base every entity (accounts, transactions, ...) maps onto.

    Columns are snake_case to match Postgres; the camelCase boundary lives in
    API-layer Pydantic schemas, never here (CONTRIBUTING.md "Casing").
    """
