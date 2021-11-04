from nautils import naPlugin

from nautils.config import GetValue


class aPlugin(naPlugin):
    def load(self, ctx):
        super(aPlugin, self).load(ctx)

    @naPlugin.listen("MessageCreate")
    def a_listener(self, event):
        if GetValue('options.a.enabled', False):
            return

        if event.channel.id != GetValue('options.a.cid', None):
            return

        if event.author.id in GetValue('options.a.exception', []):
            return

        if 'a' != event.content:
            event.delete()
