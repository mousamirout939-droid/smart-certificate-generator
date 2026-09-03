import random
import string
from datetime import datetime

from sqlalchemy.orm import Session


def generate_certificate_id(db: Session) -> str:
    """
    Generate a collision-safe, unique certificate ID in the form:
        CERT-<YEAR>-<6 random alphanumeric chars>

    Retries with a fresh random suffix if a collision is somehow found.
    """
    from app.models.certificate import Certificate  # local import avoids circular import

    year = datetime.utcnow().year
    alphabet = string.ascii_uppercase + string.digits

    for _ in range(20):
        suffix = "".join(random.choices(alphabet, k=6))
        candidate = f"CERT-{year}-{suffix}"
        exists = db.query(Certificate).filter(Certificate.certificate_id == candidate).first()
        if not exists:
            return candidate

    raise RuntimeError("Failed to generate a unique certificate ID after 20 attempts")
