from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
"""
User  1:n   Todo
"""


class User(db.Model):
    __tablename__ = 'users'
    # 自增的主键
    id = db.Column(db.Integer, primary_key=True)
    # 邮箱必须唯一，且不能为空
    email = db.Column(db.String(100),unique=True,nullable=False)
    # 密码不能为空
    password = db.Column(db.String(255),nullable=False)
    # 创建关系映射，用来反向查找（通过todo对象找todo对应的user对象
    # 一个user可以创建多个todo
    # 使用db.relationship创建 User和Todo模型的关联
    # 例如：我们可以这样新建一个todo
    # todo = Todo(text='something')
    # user = User.query.get(1)
    # todo.creator = user   # 创建者 和  所创建的todo的关联
    # db.session.add(todo)
    # db.session.commit()
    todos = db.relationship('Todo',backref="creator")

    def __init__(self,email,password):
        self.email = email
        self.password = password


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(200),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    is_done = db.Column(db.Boolean)
    # 一个todo只属于一个User
    creator_id = db.Column(
        # 外健关联users表中id
        db.Integer,db.ForeignKey('users.id'),nullable=True
    )

    def to_dict(self):
        return dict(
            id=self.id,
            text=self.text,
            created_at = self.created_at,
            creator_id = self.creator_id,
            is_done=self.is_done
        )