import functools
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from stdhomework.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')


# 根据 id 获取 system_notice 表中的数据
@bp.route('/system_notice/<int:id>', methods=['GET'])
def get_system_notice(id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("SELECT * FROM system_notice WHERE id = %s", (id,))
    result = cursor.fetchone()
    print(result)
    if not result:
        return jsonify({'error': '未找到指定的系统通知'}), 404
    return jsonify({'id': result['id'], 'title': result['title'], 'content': result['content'],
                    'create_time': result['create_time'], 'admin_id': result['admin_id']}), 200


# 向 system_notice 表中插入数据
@bp.route('/system_notice', methods=['POST'])
def create_system_notice():
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取数据
    title = data['title']
    content = data['content']
    admin_id = data['admin_id']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 插入新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("INSERT INTO system_notice (title, content, create_time, admin_id) VALUES (%s, %s, %s, %s)",
                   (title, content, create_time, admin_id))
    db.commit()

    # 返回信息
    return jsonify({'message': '系统通知创建成功'}), 201


# 根据 id 更新 system_notice 表中的数据
@bp.route('/system_notice/<int:id>', methods=['PUT'])
def update_system_notice(id):
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取数据
    title = data['title']
    content = data['content']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    admin_id = data['admin_id']

    # 更新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("UPDATE system_notice SET title = %s, content = %s, create_time = %s, admin_id = %s WHERE id = %s",
                   (title, content, create_time, admin_id, id))
    db.commit()

    # 返回信息
    return jsonify({'message': '系统通知更新成功'}), 200


# 根据 id 删除 system_notice 表中的数据
@bp.route('/system_notice/<int:id>', methods=['DELETE'])
def delete_system_notice(id):
    # 删除数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("DELETE FROM system_notice WHERE id = %s", (id,))
    db.commit()

    # 返回信息
    return jsonify({'message': '系统通知删除成功'}), 200


# 定义获取学生信息的 API,可通过学生的姓名和班级查看
@bp.route('/students', methods=['GET'])
def get_students():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    std_name = request.args.get('std_name')
    class_name = request.args.get('class_name')

    # 构建 SQL 查询语句
    conditions = []
    if std_name:
        conditions.append(f"name = '{std_name}'")
    if class_name:
        conditions.append(f"class_name = '{class_name}'")

    if conditions:
        # 有查询条件，按条件查询学生信息
        where_clause = " AND ".join(conditions)  # 使用 AND 连接列表中的每一个元素
        sql = f"SELECT * FROM studentinfo WHERE {where_clause}"
    else:
        # 没有查询条件，查询所有学生信息
        sql = "SELECT * FROM studentinfo"

    # 执行 SQL 查询语句
    cursor.execute(sql)

    # 获取查询结果
    students = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 没有查询到任何学生记录，返回 404 错误响应
    if len(students) == 0:
        return jsonify({'error': '未找到任何学生信息'}), 404

    # 返回查询结果
    return jsonify({'students': students}), 200


# 定义获取单个学生信息的 API
@bp.route('/students/<string:stu_id>', methods=['GET'])
def get_student(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT * FROM studentinfo WHERE stu_id = "{stu_id}"')

    # 获取查询结果
    student = cursor.fetchone()

    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not student:
        return jsonify({'error': f'未找到 ID 为 {stu_id} 的学生信息'}), 404

    # 返回查询结果
    return jsonify({'student': student}), 200


# 定义添加学生信息的 API
@bp.route('/students', methods=['POST'])
def add_student():
    # 获取 POST 请求上传的数据
    stu_id = request.json['stu_id']
    name = request.json['name']
    class_name = request.json['class_name']
    email = request.json['email']
    telephone = request.json['telephone']

    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 插入新的学生信息
    cursor.execute(f'INSERT INTO studentinfo (stu_id, name, class_name, email, telephone) VALUES '
                   f'("{stu_id}", "{name}", "{class_name}", "{email}", "{telephone}")')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'message': '学生信息添加成功'}), 201


# 定义更新学生信息的 API
@bp.route('/students/<string:stu_id>', methods=['PUT'])
def update_student(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 查询指定的学生信息是否存在
    cursor.execute(f'SELECT * FROM studentinfo WHERE stu_id = "{stu_id}"')
    student = cursor.fetchone()

    # 如果学生信息不存在，则返回 404 错误
    if not student:
        return jsonify({'error': f'未找到 ID 为 {stu_id} 的学生信息'}), 404

    # 更新学生信息
    name = request.json.get('name', student['name'])
    class_name = request.json.get('class_name', student['class_name'])
    email = request.json.get('email', student['email'])
    telephone = request.json.get('telephone', student['telephone'])

    cursor.execute(
        f'UPDATE studentinfo SET name = "{name}", class_name = "{class_name}", email = "{email}", telephone = "{telephone}" WHERE stu_id = "{stu_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'message': f'ID 为 {stu_id} 的学生信息已更新'}), 200


# 定义删除学生信息的 API
@bp.route('/students/<string:stu_id>', methods=['DELETE'])
def delete_student(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT * FROM studentinfo WHERE stu_id = "{stu_id}"')

    # 获取查询结果
    student = cursor.fetchone()

    # 如果查询结果为空，则返回 404 错误
    if not student:
        return jsonify({'error': f'未找到 ID 为 {stu_id} 的学生信息'}), 404

    # 删除学生信息
    cursor.execute(f'DELETE FROM studentinfo WHERE stu_id = "{stu_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'message': f'ID 为 {stu_id} 的学生信息已删除'}), 200
