from app import create_app, db
from app.models import User, Person

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Person': Person}
