from nautils import naPlugin

from nautils.config import Getcfgvalue


class aPlugin(naPlugin):
    def load(self, ctx):
        super(aPlugin, self).load(ctx)

    @naPlugin.listen('MessageCreate')
    def a_listener(self, event):
        self.log.info("f")
        if Getcfgvalue('options.a.enabled', False):
            return
        self.log.info("u")
        if event.channel.id != Getcfgvalue('options.a.cid', None):
            return
        self.log.info("c")
        if event.author.id in Getcfgvalue('options.a.exception', []):
            return
        self.log.info("k")
        if 'a' != event.content:
            event.delete()
