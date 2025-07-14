from flask import Flask
from config import Config
from flask_login import LoginManager
from .models import db, User, Admin
from werkzeug.security import generate_password_hash
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from . import routes
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            default_admin = Admin(
                username='admin',
                password=generate_password_hash('admin123')  # mật khẩu mặc định
            )
            db.session.add(default_admin)
            db.session.commit()
            print("✅ Đã tạo tài khoản admin mặc định (username: admin / password: admin123)")

    from . import routes
    return app