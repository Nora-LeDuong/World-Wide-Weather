from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), nullable=False)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SearchHistory {self.city_name}>'

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), nullable=False, unique=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Favorite {self.city_name}>'
