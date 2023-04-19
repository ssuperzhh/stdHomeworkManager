from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

# from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('teacher', __name__, url_prefix='/teacher')


# 查看教师课程列表
@bp.route('<string:tea_id>/courses', methods=['GET'])
def get_teacher_courses(tea_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 tea_id 查询教师课表
    cursor.execute(f'SELECT courseinfo.*'
                   f' FROM courseinfo WHERE tea_id = "{tea_id}"')

    # 获取查询结果
    teacher_courses = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not teacher_courses:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {tea_id} 的教师的课表信息'})

    # 返回查询结果
    return jsonify({'code': 0, 'data': teacher_courses, 'msg': ""})


# 更新密码
@bp.route('/update_pwd/<string:tea_id>', methods=['PUT'])
def update_teacher(tea_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    cursor.execute(f'SELECT * FROM user WHERE identity_id = "{tea_id}"')
    student = cursor.fetchone()

    if not student:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {tea_id} 的信息'})

    # 更新学生信息
    new_password = request.json.get('new_password', student['name'])
    cursor.execute(
        f'UPDATE user SET password = "{new_password}" WHERE identity_id = "{tea_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {tea_id} 的密码已更新'})


# 答案自动批阅
@bp.route('/correct/<int:homework_id>/<string:student_id>', methods=['GET'])
def correct_normal_homework(homework_id, student_id):
    db = get_db()
    cursor = db.cursor()
    score = 0
    try:
        cursor.execute(f'SELECT * FROM student_question WHERE homework_id={homework_id} and student_id="{student_id}"')
        stu_homework = cursor.fetchall()
        cursor.execute(f'SELECT * FROM questioninfo WHERE homework_id={homework_id}')
        question_info = cursor.fetchall()
        for item in stu_homework:
            for jtem in question_info:
                if jtem['id'] == item['question_id']:
                    if item['answer'] == jtem['truth']:
                        score += jtem['question_score']

        cursor.close()
        # 返回成功信息
        return jsonify({'code': 200, 'msg': '', 'score': score})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})


# 将批阅的分数提交
@bp.route('/submit_score', methods=['POST'])
def submit_score():
    db = get_db()
    cursor = db.cursor()
    # 解析请求中的 JSON 数据
    data = request.get_json()
    homework_id = data['homework_id']
    student_id = data['student_id']
    score = data['score']
    try:
        sql = f'UPDATE student_homework SET score={score} WHERE homework_id={homework_id} AND student_id="{student_id}"'
        cursor.execute(sql)
        cursor.close()
        db.commit()
        # 返回成功信息
        return jsonify({'code': 200, 'msg': f'分数为{score},批改成功'})
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'code': 500, 'msg': str(e)})


import random

#相似题目推荐
@bp.route('/question_recommend', methods=['GET'])
def question_recommend():
    db = get_db()
    cursor = db.cursor()
    # 解析请求中的 JSON 数据
    question_type = request.args.get('question_type')
    knowledge = request.args.get('knowledge')
    question_id = int(request.args.get('question_id'))
    try:
        sql = f'SELECT * FROM questioninfo WHERE type="{question_type}" AND knowledge="{knowledge}" AND id!={question_id}'
        cursor.execute(sql)
        recommend_questions = cursor.fetchall()
        if recommend_questions:
            recommend_question = random.choice(recommend_questions)
            cursor.close()
            # 返回成功信息
            return jsonify({'code': 200, 'msg': '', 'data': recommend_question})
        else:
            return jsonify({'code': 404, 'msg': '未查询到相似题目', 'data': ''})
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'code': 500, 'msg': str(e)})


#相似题目推荐的答案
@bp.route('/question_recommend_answer', methods=['GET'])
def question_recommend_answer():
    db = get_db()
    cursor = db.cursor()
    # 解析请求中的 JSON 数据
    request_question_id = request.args.get('question_id')
    question_id = int(request_question_id.split('_')[1])
    try:
        sql = f'SELECT * FROM questioninfo WHERE  id={question_id}'
        cursor.execute(sql)
        truth = cursor.fetchall()
        cursor.close()
        # 返回成功信息
        return jsonify({'code': 0, 'msg': '', 'data': truth})
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'code': 500, 'msg': str(e)})
