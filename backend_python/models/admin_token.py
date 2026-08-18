from datetime import datetime, timezone

from extensions import db


class AdminToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    admin_user_id = db.Column(db.Integer, db.ForeignKey("admin_user.id"), nullable=True)
