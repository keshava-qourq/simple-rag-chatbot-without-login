# ENVIRONMENT

Written by Dex. Do not edit: Dex rewrites this file whenever the project's service list changes.

How this project's code reaches its backing services. Every connection setting is an environment variable named below. The sandbox provides the values (the deployment does in production); never write a value into code, tests, config files or this repository.

Check every connection from the app's own code:

```sh
backend/.venv/bin/python backend/scripts/check_connections.py
```

## PostgreSQL

The app's relational database.

| Variable | Holds |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL of the database, password included |

```python
import os

from sqlalchemy import create_engine, text

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
```

Tests use the real PostgreSQL the sandbox runs (same `DATABASE_URL`); no mocks, no SQLite stand-in.

## pgvector (vectors in PostgreSQL)

Vector columns and similarity search in the same PostgreSQL database; the `vector` extension is already created.

| Variable | Holds |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL of the database, password included |

```python
import os

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    embedding = Column(Vector(1536))
```

Tests use the real PostgreSQL with `vector` the sandbox runs; no mocks.

## Object storage (MinIO, S3-compatible)

File storage through the S3 API; in the sandbox a MinIO server with one bucket.

| Variable | Holds |
|---|---|
| `S3_BUCKET` | the bucket to use |
| `S3_ENDPOINT_URL` | the MinIO server's URL |
| `AWS_REGION` | the region the client signs for |
| `AWS_ACCESS_KEY_ID` | access key |
| `AWS_SECRET_ACCESS_KEY` | secret key |

```python
import os

import boto3
from botocore.config import Config

endpoint = os.environ.get("S3_ENDPOINT_URL") or None  # set for MinIO, unset for AWS S3
s3 = boto3.client(
    "s3",
    region_name=os.environ["AWS_REGION"],
    endpoint_url=endpoint,
    config=Config(s3={"addressing_style": "path"}) if endpoint else None,
)  # credentials come from the AWS_* variables automatically
bucket = os.environ["S3_BUCKET"]
s3.put_object(Bucket=bucket, Key="example.txt", Body=b"hello")
```

Tests use the real bucket the sandbox runs (same variables); no mocks, no moto.
