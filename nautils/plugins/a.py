from nautils import naPlugin

from nautils.config import Getcfgvalue


class aPlugin(naPlugin):
    def load(self, ctx):
        super(aPlugin, self).load(ctx)

    @naPlugin.listen("MessageCreate")
    def a_listener(self, event):
        if Getcfgvalue('options.a.enabled', False):
            return

        if event.channel.id != Getcfgvalue('options.a.cid', None):
            return

        if event.author.id in Getcfgvalue('options.a.exception', []):
            return

        if 'a' != event.content:
            event.delete()
