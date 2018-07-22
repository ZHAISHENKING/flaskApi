from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from todos.models import db,Todo
from todos.app import create_app
# 创建 app 实例
app = create_app()
# 创建migrate实例
migrate = Migrate(app,db)
# 创建 manage实例
manager = Manager(app)
# 提供一个migration命令
manager.add_command('db', MigrateCommand)


# 启用python shell
@manager.shell
def shell_ctx():
    return dict(
        app=app,
        db=db,
        Todo=Todo
    )


if __name__ == '__main__':
    manager.run()