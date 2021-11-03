from nautils import naPlugin

from nautils.config import options


class aPlugin(naPlugin):
    def load(self, ctx):
        super(aPlugin, self).load(ctx)

    @naPlugin.listen("MessageCreate")
    def a_listener(self, event):
        if not options['a']['enabled']:
            return

        if event.channel.id != options['a']['cid']:
            return

        if event.author.id in options['a']['exception']:
            return

        if 'a' != event.content:
            event.delete()
