
def cleanup_expired_records() -> None:
    import os
    import sys
    from datetime import datetime, timezone
    from pathlib import Path

    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))

    from database.database import SessionLocal
    from database.models import UserActivationTokens, UserSession

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    with SessionLocal.begin() as db:
        db.query(UserSession).filter(UserSession.expires_at <= now).delete(synchronize_session=False)
        db.query(UserActivationTokens).filter(UserActivationTokens.expires_at <= now).delete(synchronize_session=False)
        
    print("Cleanup completed.")


