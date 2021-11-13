from flask import send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from nautils import naPlugin
from nautils.config import Getcfgvalue
from nautils.routes import join


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
        global bot
        bot = self.bot
        self.init_api()

    def init_api(self):
        if Getcfgvalue("web.secret_key", None):
            secret_key = Getcfgvalue("web.secret_key", None)
        else:
            secret_key = genkey()

        self.bot.http.secret_key = bytes(secret_key, 'utf8')
        self.bot.http.config['MAX_CONTENT_LENGTH'] = (16 * 1024 * 1024)
        self.bot.http.wsgi_app = ProxyFix(self.bot.http.wsgi_app, x_host=1)
        self.bot.http.register_blueprint(join)

    @bot.http.route('/')
    def auth_discord(self):
        return send_from_directory('nautils/www/dmeta.html')