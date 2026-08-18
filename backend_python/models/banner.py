from extensions import db


class Banner(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    image = db.Column(db.String(500), default="")
    title = db.Column(db.String(200), default="")
    link = db.Column(db.String(500), default="")
    order = db.Column(db.Integer, default=0)
    sortWeight = db.Column(db.Integer, default=0)
