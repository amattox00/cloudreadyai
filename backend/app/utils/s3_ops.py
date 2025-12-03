import logging
import os
from typing import BinaryIO, Optional

logger = logging.getLogger(__name__)


def get_s3_bucket_name() -> Optional[str]:
    """
    Returns the bucket name for CloudReadyAI ingest, if set.

    In real environments this would come from CLOUDREADY_S3_BUCKET.
    For now we treat it as optional so dev doesn't crash if it's missing.
    """
    return os.getenv("CLOUDREADY_S3_BUCKET")


def s3_upload_fileobj(
    fileobj: BinaryIO,
    key: Optional[str] = None,
    content_type: Optional[str] = None,
) -> str:
    """
    Dev/stub implementation of an S3 upload.

    - Accepts an open binary file-like object.
    - Optionally accepts an S3-style key; if not provided, generates one.
    - Returns the key we *would* have used.

    For Phase B1 we *do not* actually talk to AWS S3 yet — this is a no-op
    that just logs the intent so the rest of the ingestion pipeline can
    be built and tested safely.
    """
    bucket = get_s3_bucket_name()

    if not key:
        # Simple deterministic placeholder. Later we’ll make this
        # something like f"runs/{run_id}/vcenter/{uuid4()}.csv"
        key = "mock/ingest/vcenter_upload.csv"

    # Consume the fileobj to mimic real upload behavior
    try:
        # Make sure we're at the start
        if hasattr(fileobj, "seek"):
            fileobj.seek(0)
        # Read the content once (and discard); this is just to mimic streaming
        _ = fileobj.read()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Mock S3 upload: failed to read fileobj: %s", exc)

    logger.info(
        "Mock S3 upload (no-op): bucket=%s key=%s content_type=%s",
        bucket,
        key,
        content_type,
    )

    # Return the pretend key so callers can record it against the run
    return key
