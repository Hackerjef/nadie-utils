import re

from nautils import naPlugin

from nautils.config import Getcfgvalue


# noinspection PyAttributeOutsideInit
class Specialchannel(naPlugin):
    def load(self, ctx):
        self.A_RE = re.compile(r"a")
        self.EMOJI_RE = re.compile(r"<a:.+?:\d+>|<:.+?:\d+>")
        super(Specialchannel, self).load(ctx)

    def ca(self, event, execption: list):
        if event.author.id in execption + Getcfgvalue('options.special_channels.a.exception', []):
            return

        if not event.content:
            return event.delete()

        if re.sub(self.A_RE, "", event.content.replace(" ", "").lower()):
            return event.delete()

    def cbongo(self, event, execption: list):
        if event.author.id in execption + Getcfgvalue('options.special_channels.bongo.exception', []):
            return

        if not event.content:
            return event.delete()

        if re.sub(self.EMOJI_RE, "", event.content.replace(" ", "")):
            return event.delete()

        for emote in re.findall(self.EMOJI_RE, event.content):
            if "bongo" not in emote.lower():
                return event.delete()

    def cban(self, event, execption: list):
        if event.author.bot:
            return event.delete()

        if event.author.id in execption + Getcfgvalue('options.special_channels.ban.exception', []):
            return

        invite = self.bot.client.state.channels.get(Getcfgvalue('options.special_channels.ban.invite_cid', None),
                                                    None).create_invite(max_age=60, max_uses=1, unique=True)
        event.delete()
        try:
            event.author.open_dm().send_message(
                f"Why did you think that was a good idea, here:\n you have 60s before its invalid and then you have to go through oauth:\n<{invite.link}>\n<https://d.nadie.dev/join>")
        except:
            pass
        event.guild.get_member(event.author).ban(reason="banned channel")
        event.guild.delete_ban(event.author.id)

    def cdad(self, event, exception: list):
        if event.author.bot:
            return event.delete()

        if not event.content:
            return event.delete()

        if event.author.id in exception + Getcfgvalue('options.special_channels.dad.exception', []):
            return

        event.msg.reply(f"HI! {event.content}")

    def abuse(self, event, execption: list):
        if event.author.id in execption:
            return

        if event.author.bot:
            return

        return event.reply("\"absue\" https://i.nadie.dev/1K85OtG.png")

    @naPlugin.listen('MessageCreate')
    @naPlugin.listen('MessageUpdate')
    def special_listener(self, event):
        # exception list
        pexception = Getcfgvalue('options.special_channels.pexception', [])

        # A listener
        if event.channel.id == Getcfgvalue('options.special_channels.a.cid', None):
            if Getcfgvalue('options.special_channels.a.enabled', False):
                return self.ca(event, pexception)
            return

        # bongo listener
        if event.channel.id == Getcfgvalue('options.special_channels.bongo.cid', None):
            if Getcfgvalue('options.special_channels.bongo.enabled', False):
                return self.cbongo(event, pexception)
            return

        # Ban listener
        if event.channel.id == Getcfgvalue('options.special_channels.ban.cid', None):
            if Getcfgvalue('options.special_channels.ban.enabled', False):
                return self.cban(event, pexception)
            return

        if event.channel.id == Getcfgvalue('options.special_channels.dad.cid', None):
            if Getcfgvalue('options.special_channels.dad.enabled', False):
                return self.cdad(event, pexception)
            return
