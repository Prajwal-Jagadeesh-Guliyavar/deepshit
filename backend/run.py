from app import create_app, db
from app.models import User, MedicalReport
from app.routes import jwt

app = create_app()
jwt.init_app(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'MedicalReport': MedicalReport}

if __name__ == '__main__':
    app.run(debug=True)