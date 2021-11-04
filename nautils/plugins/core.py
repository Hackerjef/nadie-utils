import os
import pprint
import signal

from datetime import datetime

from disco.bot import CommandLevels
from disco.bot.command import CommandEvent
from disco.types.channel import ChannelType
from disco.types.permissions import Permissions

from nautils import naPlugin
from nautils.config import Getcfgvalue
from nautils.utils import parse_natural, get_level


PY_CODE_BLOCK = u'```py\n{}\n```'


class CorePlugin(naPlugin):
    def load(self, ctx):
        super(CorePlugin, self).load(ctx)

        # noinspection PyAttributeOutsideInit
        self.startup = ctx.get('startup', datetime.utcnow())

    @naPlugin.listen('Ready')
    def on_ready(self, event):
        self.log.info(f"{len(event.guilds)} guilds in shard {self.client.config.shard_id}")

    @naPlugin.listen('MessageCreate')
    def on_message_command(self, event):
        if event.message.author.bot:
            return

        if event.message.channel.type in (ChannelType.DM, ChannelType.GROUP_DM):
            return

        if not event.message.channel.get_permissions(self.state.me).can(Permissions.SEND_MESSAGES):
            return

        commands = list(self.bot.get_commands_for_message(False, {}, Getcfgvalue("options.prefix", ['!']), event.message))

        if not len(commands):
            return

        # Grab level of user
        level = get_level(event.guild, event.author)

        for command, match in commands:
            clevel = command.level or 0  # 0

            if clevel > level:
                continue

            command_event = CommandEvent(command, event.message, match)
            command.plugin.execute(command_event)

    @naPlugin.command('uptime', level=CommandLevels.MOD)
    def command_uptime(self, event):
        event.msg.reply(':stopwatch: Bot was started `{}` ago.'.format(parse_natural(datetime.utcnow() - self.startup)))

    @naPlugin.command('ping', level=CommandLevels.MOD)
    def cmd_ping(self, event):
        return event.msg.reply("Current Ping: **{}** ms".format(round(self.client.gw.latency, 2)))

    @naPlugin.command('eval', level=CommandLevels.OWNER)
    def cmd_eval(self, event):
        """
        This a Developer command which allows us to run code without having to restart the bot.
        """
        ctx = {
            'bot': self.bot,
            'shards': self.bot.shards,
            'client': self.bot.client,
            'state': self.bot.client.state,
            'event': event,
            'msg': event.msg,
            'guild': event.msg.guild,
            'channel': event.msg.channel,
            'author': event.msg.author
        }

        # Mulitline eval
        src = event.codeblock
        if src.count('\n'):
            lines = list(filter(bool, src.split('\n')))
            if lines[-1] and 'return' not in lines[-1]:
                lines[-1] = 'return ' + lines[-1]
            lines = '\n'.join('    ' + i for i in lines)
            code = 'def f():\n{}\nx = f()'.format(lines)
            local = {}

            try:
                exec(compile(code, '<eval>', 'exec'), ctx, local)
            except Exception as e:
                event.msg.reply(PY_CODE_BLOCK.format(
                    type(e).__name__ + ': ' + str(e)))
                return

            result = pprint.pformat(local['x'])
        else:
            try:
                result = str(eval(src, ctx))
            except Exception as e:
                event.msg.reply(PY_CODE_BLOCK.format(
                    type(e).__name__ + ': ' + str(e)))
                return

        if len(result) > 1990:
            event.msg.reply('', attachments=[('result.txt', result)])
        else:
            event.msg.reply(PY_CODE_BLOCK.format(result))