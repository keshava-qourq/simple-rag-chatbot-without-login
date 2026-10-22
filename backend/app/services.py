"""The backing services this application is configured to reach.

Each entry maps a service to the environment variable that addresses it. The value
comes from docker-compose.yml through .env.example, so the health check reports
what the running deployment can actually reach.
"""

import os

from minio import Minio

SERVICES = {
    "minio": "MINIO_ENDPOINT",
}


def configured_services() -> dict[str, bool]:
    """Each service mapped to whether its connection variable is set."""
    return {name: bool(os.getenv(var)) for name, var in SERVICES.items()}


def minio_client() -> Minio:
    """A client for the MinIO deployment named in the environment.

    A FastAPI dependency rather than a module-level singleton, so tests can
    override it with a fake and never touch a real object store.
    """
    return Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", ""),
        secret_key=os.getenv("MINIO_SECRET_KEY", ""),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )


def minio_bucket() -> str:
    """The bucket uploaded documents are stored in."""
    return os.getenv("MINIO_BUCKET", "documents")
