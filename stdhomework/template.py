import functools
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from stdhomework.db import get_db

bp = Blueprint('template', __name__, url_prefix='/template')

@bp.route('/')
def index():
    return render_template('admin/index.html')