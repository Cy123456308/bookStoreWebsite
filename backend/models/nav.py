from datetime import datetime
from extensions import db


class NavItem(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    to = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
