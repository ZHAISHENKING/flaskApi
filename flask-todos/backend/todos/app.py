from flask import Flask


def create_app(app_name="TODO_API"):
    app = Flask(app_name)
    app.config.from_object('todos.config')
    from todos.api import api
    # 注册蓝图
    app.register_blueprint(api, url_prefix='/api')
    from todos.models import db
    # 初始化app
    db.init_app(app)
    return app