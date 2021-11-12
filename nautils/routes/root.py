from flask import Blueprint, redirect, request, send_from_directory

root = Blueprint('root', __name__, url_prefix='/')


@root.route('/')
def root():
    if "discord" in str(request.headers.get('User-Agent')).lower():
        return send_from_directory('nautils/www/dmeta.html')

    return redirect("https://youtu.be/LDU_Txk06tM?t=75")