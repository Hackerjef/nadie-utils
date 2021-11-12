from flask import Blueprint, redirect

join = Blueprint('root', __name__, url_prefix='/')


@join.route('/')
def root():
    return redirect("https://youtu.be/LDU_Txk06tM?t=75")