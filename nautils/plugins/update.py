import hmac
import os

import git
from disco.bot import CommandLevels
from flask import request, abort, jsonify
from gevent import subprocess

from nautils import naPlugin
from nautils.config import Getcfgvalue
from nautils.utils import Get_Hash

PY_CODE_BLOCK = u'```py\n{}\n```'


# Lol test

# noinspection PyAttributeOutsideInit
class UpdatePlugin(naPlugin):
    def load(self, ctx):
        self.grepo = git.cmd.Git(os.getcwd())
        self.spawn_later(5, self.update_bot)
        super(UpdatePlugin, self).load(ctx)

    def update_bot(self, event=None):
        self.log.info(f"Update triggered by {'user' if event else 'git push'}.")
        pipfile_hash = Get_Hash("Pipfile.lock")
        gpull = self.grepo.pull()
        if gpull == "Already up to date.":
            if event:
                event.msg.reply("Repo up to date")
            self.log.info("Repo already up to date, no need to update")
            return

        if event:
            event.msg.reply(PY_CODE_BLOCK.format(gpull))

        if pipfile_hash != Get_Hash("Pipfile.lock"):
            self.log.info("Updating/installing Dependencies")
            m = None
            if event:
                m = event.msg.reply("Updating/installing Dependencies...")
            p = subprocess.check_output(["env", "CI=true", "pipenv", "--bare", "install"]).decode("utf-8", "ignore")
            if m:
                m.edit(PY_CODE_BLOCK.format(p))
        if event:
            event.msg.reply("Bot restarting")
        self.log.info("Restarting bot due to update!")
        self.bot.plugins['ControlPlugin'].ProcessControl(signalNumber=2)

    @naPlugin.route("/autoupdate", strict_slashes=False, methods=['POST'])
    def githublistener(self):
        if not Getcfgvalue("options.update.auto_update.enabled", False):
            self.log.warning("Got event from github, but auto update is not enabled")
            abort(404)

        # Verify responce that its from github
        if Getcfgvalue("options.update.auto_update.secret", None):
            header_signature = request.headers.get('X-Hub-Signature')
            if header_signature is None:
                abort(403)

            sha_name, signature = header_signature.split('=')
            if sha_name != 'sha1':
                abort(501)

            # HMAC requires the key to be bytes, but data is string
            mac = hmac.new(bytes(Getcfgvalue("options.update.auto_update.secret", None), encoding='utf8'),
                           msg=request.data,
                           digestmod='sha1')
            if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
                abort(403)
        else:
            self.log.warning("GITHUB SECRET NOT SET, NOT VERFIYING GIT")

        ghevent = request.headers.get('X-GitHub-Event', 'ping')
        if ghevent == 'ping':
            return jsonify({'msg': 'pong'})

        # meh no need to 400 it if its just another event, just accept and moveon
        if not ghevent == 'push':
            return jsonify({'msg': 'Not a push event :) but its cool github just stap giving me other events'}), 200

        if not request.json:
            abort(400)

        if not request.json.get("repository", {}).get("full_name", None) == Getcfgvalue(
                "options.update.auto_update.repo", ""):
            return jsonify({'msg': 'Bot not listening for this repo'}), 400

        if not request.json.get("ref", None) == Getcfgvalue("options.update.auto_update.ref", ""):
            return jsonify({'msg': 'Bot not listening to this specific ref, silently okaying it :)'}), 200

        # check if repo, if so yeet yeet check current hash, if not same yeet (due to some updates, I have to rely on git in the update mec to handle if the bot should update or restart
        self.log.info("Queing update")
        self.spawn_later(5, self.update_bot)

        return jsonify({'status': 'done'})

    @naPlugin.command('update', level=CommandLevels.OWNER)
    def update(self, event):
        return self.update_bot(event)
