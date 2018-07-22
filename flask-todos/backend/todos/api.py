from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from .models import db, Todo, User

# pip install PyJWT
# 手动生成token
api = Blueprint('api', __name__)


@api.route('/register/', methods=['POST'])
def register():
    # 要求前端提交json格式的数据
    # 从post请求中获取json数据
    data = request.get_json()
    print(data)
    user = User(email=data['email'], password=data['password'])
    # user = User(**data)
    db.session.add(user)
    db.session.commit()
    msg = {"msg": "注册成功!"}
    return jsonify(msg), 201


@api.route('/todos/', methods=['POST'])
def create_todo():
    """
    {
        "content":"10分钟下课
    }
    """
    user = User.query.get(1)  # 获取id为1的用户
    data = request.get_json()

    todo = Todo(text=data['content'])
    todo.creator = user
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@api.route('/todos/', methods=['GET'])
def fetch_todos():
    todos = Todo.query.all()
    user = User.query.get(1)
    todos = user.todos  # 获得用户  user的所有todo
    return jsonify([todo.to_dict() for todo in todos])


@api.route('/todos/<int:id>/', methods=['GET','PUT','DELETE'])
def todo_detail(id):
    msg = {
        'message':None
    }
    todo = Todo.query.get(id)
    # 前端请求 /todos/1/ GET 返回id为1的todo
    if request.method == 'GET':
        return jsonify(todo.to_dict()),201
    elif request.method == 'PUT':
        # 获取新的值
        data = request.get_json()
        todo.text = data.get('content')
        db.session.add(todo)
        db.session.commit()
        return jsonify(todo.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(todo)
        db.session.commit()
        msg['message'] = '删除成功!'
        return jsonify(msg)