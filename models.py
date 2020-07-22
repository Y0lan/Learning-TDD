from app import db


class Flaskr(db.Model):

    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String, nullable=False)
    contenu = db.Column(db.String, nullable=False)

    def __init__(self, titre, contenu):
        self.titre = titre
        self.contenu = contenu

    def __repr__(self):
        return f'<titre: {self.body}>'