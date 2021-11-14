import os

from flask import send_file, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from nautils import naPlugin
from nautils.config import Getcfgvalue


def genkey():
    from secrets import choice
    import string
    key = ''.join([choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(50)])
    print("Cannot grab flask secret key from env, Generating a temp one")
    print("Use this key in Env if you want to presist sessions:\n" + key)
    return key


class webPlugin(naPlugin):
    def load(self, ctx):
        super(webPlugin, self).load(ctx)
        if self.bot.client.config.shard_id != 0:
            return self.unload(ctx)

        if Getcfgvalue("web.secret_key", None):
            secret_key = Getcfgvalue("web.secret_key", None)
        else:
            secret_key = genkey()

        self.bot.http.secret_key = bytes(secret_key, 'utf8')
        self.bot.http.config['MAX_CONTENT_LENGTH'] = (16 * 1024 * 1024)
        self.bot.http.wsgi_app = ProxyFix(self.bot.http.wsgi_app, x_host=1)

    @naPlugin.route("/")
    def webroot(self):
        return send_file(os.getcwd() + '/nautils/www/dmeta.html')

    @naPlugin.route('/robots.txt')
    def noindex(self):
        r = Response(response="User-Agent: *\nDisallow: /\n", status=200, mimetype="text/plain")
        r.headers["Content-Type"] = "text/plain; charset=utf-8"
        return r
