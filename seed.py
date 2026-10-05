"""Run after `flask --app run db upgrade`."""

from app import create_app
from app.cli import seed_demo

if __name__ == "__main__":
    with create_app().app_context():
        seed_demo()
