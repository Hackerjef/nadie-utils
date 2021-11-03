from disco.bot import Plugin

from nautils.config import options


class aPlugin(Plugin):
    def load(self, ctx):
        super(aPlugin, self).load(ctx)

    @Plugin.listen("MessageCreate")
    def a_listener(self, event):
        if not options['a']['enabled']:
            return

        if event.channel.id != options['a']['cid']:
            return

        if event.author.id in options['a']['exception']:
            return

        if 'a' == event.msg.content:
            event.delete()
