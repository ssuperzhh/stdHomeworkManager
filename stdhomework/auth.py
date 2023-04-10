import functools
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from stdhomework.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# @bp.route('/')
# def hello_world():  # put application's code here
#     db = get_db()
#     # 创建一个 cursor 对象
#     cur = db.cursor()
#     # 执行 SELECT 语句
#     cur.execute("SELECT * FROM user")
#
#     # 获取所有结果集
#     results = cur.fetchall()
#
#     return results

# 注册接口
@bp.route('/register', methods=['POST'])
def register():
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取用户名、密码和邮箱
    username = data['name']
    password = data['password']
    email = data['email']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 检查用户名是否已存在
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE name=%s", (username,))
    result = cursor.fetchone()
    if result:
        return jsonify({'error': '用户名已存在'}), 400

    # 插入新用户数据
    cursor.execute("INSERT INTO user (name, password, email, create_time) VALUES (%s, %s, %s, %s)",
                   (username, password, email, create_time))
    db.commit()

    return jsonify({'message': '注册成功'}), 200


# 登录接口
@bp.route('/login', methods=['POST'])
def login():
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取用户名和密码
    username = data['username']
    password = data['password']
    identity = data['identity']

    # 检查用户名和密码是否匹配
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE name=%s AND password=%s AND identity=%s", (username, password, identity))
    result = cursor.fetchone()
    if not result:
        return jsonify({'code': 500, 'msg': '用户名或密码或身份错误'})

    # 将用户的 ID 存入 session
    session['user_id'] = result['id']
    session['identity'] = result['identity']
    # 返回成功登录的信息
    return jsonify({'code': 200, 'msg': '登录成功'})


# 登出接口
@bp.route('/logout', methods=['POST'])
def logout():
    # 删除 session 中的用户 ID
    session.pop('user_id', None)
    session.pop('identity', None)

    return jsonify({'code': 200, 'msg': '退出成功'})

#
# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#         create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         db = get_db()
#         cur = db.cursor()
#         error = None
#
#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#         elif not email:
#             error = 'Email is required.'
#
#         if error is None:
#             try:
#                 cur.execute("INSERT INTO user (name, password, email,create_time) VALUES (%s, %s, %s, %s)",
#                             (username, password, email, create_time))
#                 db.commit()
#                 cur.close()
#             except db.IntegrityError:
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for("auth.login"))
#
#         flash(error)
#
#     return render_template('auth/register.html')
#
#
# @bp.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         cur = db.cursor()
#         error = None
#
#         result = cur.execute('SELECT * FROM user WHERE name = %s', [username])
#         user = cur.fetchone()
#         print(user)
#         cur.close()
#         if user is None:
#             error = 'Incorrect username.'
#         else:
#             if password != user['password']:
#                 error = 'Incorrect password.'
#             else:
#                 flash('Login Successful!')
#         if error is None:
#             session.clear()
#             session['user_id'] = user['id']
#             return redirect(url_for('index'))
#         flash('Invalid username or password!')
#
#     return render_template('auth/login.html')
#
#
# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#
#     if user_id is None:
#         g.user = None
#     else:
#         cur = get_db().cursor()
#         result = cur.execute('SELECT * FROM user WHERE id = %s', (user_id,))
#         g.user = cur.fetchone()
#
#
# @bp.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))
#
#
# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))
#
#         return view(**kwargs)
#
#     return wrapped_view
