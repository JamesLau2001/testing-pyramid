from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    users = [
        User(username='admin', password=generate_password_hash('adminpass'), role='admin'),
        User(username='user', password=generate_password_hash('userpass'), role='authenticated'),
    ]

    for user in users:
        db.session.add(user)

    db.session.commit()