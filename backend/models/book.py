from extensions import db


class Book(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), default="")
    cover = db.Column(db.String(500), default="")
    price = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(50), default="")
    publishDate = db.Column(db.String(20), default="")
    category = db.Column(db.String(50), default="")
    description = db.Column(db.Text, default="")
    onSale = db.Column(db.Boolean, default=True)
    amazonUrl = db.Column(db.String(500), default="")
    relatedIds = db.Column(db.Text, default="")  # JSON
    sampleImages = db.Column(db.Text, default="")  # JSON
    sortWeight = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
