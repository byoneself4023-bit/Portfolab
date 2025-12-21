# -*- coding: utf-8 -*-
from flask import Blueprint
from controllers import auth as auth_controller

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """회원가입"""
    return auth_controller.register()


@auth_bp.route('/login', methods=['POST'])
def login():
    """로그인"""
    return auth_controller.login()


@auth_bp.route('/verify', methods=['GET'])
def verify():
    """토큰 검증"""
    return auth_controller.verify()
