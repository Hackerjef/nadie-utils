import re

from nautils import naPlugin

from nautils.config import Getcfgvalue

EMOJI_RE = re.compile(r"<a:.+?:\d+>|<:.+?:\d+>")


class bongoPlugin(naPlugin):
    def load(self, ctx):
        super(bongoPlugin, self).load(ctx)

    @naPlugin.listen("MessageCreate")
    @naPlugin.listen('MessageUpdate')
    def bongo_listener(self, event):

        if not Getcfgvalue('options.bongo.enabled', False):
            return

        if event.channel.id != Getcfgvalue('options.bongo.cid', None):
            return

        if event.author.id in Getcfgvalue('options.bongo.exception', []):
            return

        if not event.content:
            return event.delete()

        # if something
        msg = re.sub(EMOJI_RE, event.content, "")
        if msg:
            self.log.info(msg)
            return event.delete()

        self.log.info(f"emoji's found: ${re.findall(EMOJI_RE, event.content)}")
