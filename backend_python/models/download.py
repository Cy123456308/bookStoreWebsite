from extensions import db


class Download(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), default="")
    size = db.Column(db.String(50), default="")
    description = db.Column(db.Text, default="")
    publishedAt = db.Column(db.String(20), default="")
