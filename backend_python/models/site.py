from extensions import db


class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default="")
    intro = db.Column(db.Text, default="")
    twitterUrl = db.Column(db.String(500), default="")
    twitterText = db.Column(db.String(500), default="")
    email = db.Column(db.String(200), default="")
    address = db.Column(db.String(500), default="")
    phone = db.Column(db.String(100), default="")
    company = db.Column(db.Text, default="")  # JSON string
    # Business page: services & clients as JSON arrays
    services = db.Column(db.Text, default="[]")  # JSON array of strings
    clients = db.Column(db.Text, default="[]")  # JSON array of strings
    # Homepage featured sections: [{id, title, bookId}]
    homeSections = db.Column(db.Text, default="[]")  # JSON array
    logoUrl = db.Column(db.String(500), default="")
    businessLead = db.Column(db.Text, default="")
    businessIntro = db.Column(db.Text, default="")
    businessNote = db.Column(db.Text, default="")
