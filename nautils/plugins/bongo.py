from nautils import naPlugin

from nautils.config import Getcfgvalue


class bongoPlugin(naPlugin):
    def load(self, ctx):
        super(bongoPlugin, self).load(ctx)

    @naPlugin.listen("MessageCreate")
    def bongo_listener(self, event):

        if not Getcfgvalue('options.a.enabled', False):
            return

        if event.channel.id != Getcfgvalue('options.bongo.cid', None):
            return

        if event.author.id in Getcfgvalue('options.bongo.exception', []):
            return

        # @justin do ur shit here lol
