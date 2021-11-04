import os
import pprint
import signal

from disco.bot.command import CommandEvent
from disco.types.permissions import Permissions
from gevent.exceptions import BlockingSwitchOutError
from nautils.config import levels
from nautils import naPlugin

PY_CODE_BLOCK = u'```py\n{}\n```'


class CorePlugin(naPlugin):
    def load(self, ctx):
        super(CorePlugin, self).load(ctx)
        # register Process listeners
        signal.signal(signal.SIGINT, self.ProcessControl)
        signal.signal(signal.SIGTERM, self.ProcessControl)
        signal.signal(signal.SIGUSR1, self.ProcessControl)

    # @naPlugin.listen('MessageCreate')
    # def cmd_handler(self, event):
    #     print(event)
    #     if event.message.author.bot:
    #         return
    #
    #     if hasattr(event, 'guild') and event.guild:
    #         guild_id = event.guild.id
    #     elif hasattr(event, 'guild_id') and event.guild_id:
    #         guild_id = event.guild_id
    #     else:
    #         guild_id = None
    #
    #     if not guild_id:
    #         return
    #
    #     perms = event.message.channel.get_permissions(self.state.me)
    #     if not perms.can(Permissions.SEND_MESSAGES):
    #         return
    #
    #     user_level = levels[event.author.id] if event.author.id in levels else 0
    #     commands = list(self.bot.get_commands_for_message(False, {}, self.bot.config.command_prefixes, event.message))
    #
    #     if not len(commands):
    #         return
    #
    #     for command, match in commands:
    #         level = command.level or 0
    #
    #         if not user_level >= level:
    #             return
    #
    #         try:
    #             command_event = CommandEvent(command, event.message, match)
    #             command.plugin.execute(command_event)
    #         except:
    #             return event.reply('Command error')

    @naPlugin.listen('Ready')
    def on_ready(self, event):
        self.log.info(f"{len(event.guilds)} guilds in shard {self.client.config.shard_id}")

    # @naPlugin.command('ping', level=50)
    # def cmd_ping(self, event):
    #     return event.msg.reply("Current Ping: **{}** ms".format(round(self.client.gw.latency, 2)))
    #
    # @naPlugin.command('eval', level=100)
    # def cmd_eval(self, event):
    #     """
    #     This a Developer command which allows us to run code without having to restart the bot.
    #     """
    #     ctx = {
    #         'bot': self.bot,
    #         'shards': self.bot.shards,
    #         'client': self.bot.client,
    #         'state': self.bot.client.state,
    #         'event': event,
    #         'msg': event.msg,
    #         'guild': event.msg.guild,
    #         'channel': event.msg.channel,
    #         'author': event.msg.author
    #     }
    #
    #     # Mulitline eval
    #     src = event.codeblock
    #     if src.count('\n'):
    #         lines = list(filter(bool, src.split('\n')))
    #         if lines[-1] and 'return' not in lines[-1]:
    #             lines[-1] = 'return ' + lines[-1]
    #         lines = '\n'.join('    ' + i for i in lines)
    #         code = 'def f():\n{}\nx = f()'.format(lines)
    #         local = {}
    #
    #         try:
    #             exec(compile(code, '<eval>', 'exec'), ctx, local)
    #         except Exception as e:
    #             event.msg.reply(PY_CODE_BLOCK.format(
    #                 type(e).__name__ + ': ' + str(e)))
    #             return
    #
    #         result = pprint.pformat(local['x'])
    #     else:
    #         try:
    #             result = str(eval(src, ctx))
    #         except Exception as e:
    #             event.msg.reply(PY_CODE_BLOCK.format(
    #                 type(e).__name__ + ': ' + str(e)))
    #             return
    #
    #     if len(result) > 1990:
    #         event.msg.reply('', attachments=[('result.txt', result)])
    #     else:
    #         event.msg.reply(PY_CODE_BLOCK.format(result))

    def ProcessControl(self, signalNumber=None, frame=None):
        if signalNumber == 2:
            self.log.warning("Graceful shutdown initiated")
            self.client.gw.shutting_down = True
            self.client.gw.ws.close(status=4000)
            self.client.gw.ws_event.set()
            # unload plugins
            for x in list(self.bot.plugins):
                if x == 'CorePlugin':
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
