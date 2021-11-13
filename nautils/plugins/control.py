import os
import signal

import gevent.subprocess
import git

from disco.bot import CommandLevels
from gevent.exceptions import BlockingSwitchOutError

from nautils import naPlugin
from nautils.utils import Get_Hash

PY_CODE_BLOCK = u'```py\n{}\n```'


class ControlPlugin(naPlugin):
    def load(self, ctx):
        super(ControlPlugin, self).load(ctx)
        # register Process listeners
        signal.signal(signal.SIGINT, self.ProcessControl)
        signal.signal(signal.SIGTERM, self.ProcessControl)
        signal.signal(signal.SIGUSR1, self.ProcessControl)

    @naPlugin.command('update', level=CommandLevels.OWNER)
    def update(self, event):
        # thank dooley :bongo:
        pipfile_hash = Get_Hash("Pipfile.lock")

        grepo = git.cmd.Git(os.getcwd())
        gpull = grepo.pull()
        if gpull == "Already up to date.":
            return event.msg.reply("Repo up to date")
        event.msg.reply(PY_CODE_BLOCK.format(gpull))

        if pipfile_hash != Get_Hash("Pipfile.lock"):
            m = event.msg.reply("Installing packages...")
            p = gevent.subprocess.check_output(["env", "CI=true", "pipenv", "--bare", "install"]).decode("utf-8", "ignore")
            m.edit(PY_CODE_BLOCK.format(p))

        self.ProcessControl(signalNumber=2)

    def ProcessControl(self, signalNumber=None, frame=None):
        if signalNumber == 2:
            self.log.warning("Graceful shutdown initiated")
            self.client.gw.shutting_down = True
            self.client.gw.ws.close(status=4000)
            self.client.gw.ws_event.set()
            # unload plugins
            for x in list(self.bot.plugins):
                if x == 'CorePlugin' or x == 'ControlPlugin':
                    self.log.info('Skiping plugin: {}'.format(x))
                    continue
                plugin = next((v for k, v in self.bot.plugins.items() if k.lower() == x.lower()), None)
                if plugin:
                    self.log.info('Unloading plugin: {}'.format(x))
                    try:
                        self.bot.rmv_plugin(plugin)
                    except BlockingSwitchOutError:
                        self.log.warning("Plugin {} Has a active greenlet/schedule, Bruteforce".format(x))
                        # Due to the never ending disco bugs, Just remove the listeners to stop plugin execution after unload
                        plugin.greenlet = []
                        plugin.schedule = []
                        for listener in plugin.listeners:
                            listener.remove()
                        pass
                    except Exception:
                        self.log.exception("Failed to unload: {}".format(x))
        elif signalNumber == 10:  # sysuser1
            self.log.warning("Reseting shard connection to Discord")
            self.client.gw.ws.close(status=4000)
        else:
            self.log.warning("Force Shutdown initiated")
            os.kill(os.getpid(), signal.SIGKILL)
