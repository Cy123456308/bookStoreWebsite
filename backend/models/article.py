from extensions import db


class Article(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.Text, default="")
    cover = db.Column(db.String(500), default="")
    body = db.Column(db.Text, default="")
    category = db.Column(db.String(50), default="")
    publishedAt = db.Column(db.String(20), default="")
    sortWeight = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
