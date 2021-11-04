from nautils import naPlugin

from nautils.config import options

# within nautils.config lol
# options:
#   bongo:
#     enabled: true
#     cid:
#     exception: []

class bongoPlugin(naPlugin):
    def load(self, ctx):
        super(bongoPlugin, self).load(ctx)

    @naPlugin.listen("MessageCreate")
    def bongo_listener(self, event):
        if not options['bongo']['enabled']:
            return

        if event.channel.id != options['bongo']['cid']:
            return

        if event.author.id in options['bongo']['exception']:
            return

        # @justin do ur shit here lol