from disco.api.http import Routes
from disco.types.invite import Invite

from nautils import naPlugin
from nautils.config import Getcfgvalue


class ucommandsPlugin(naPlugin):
    def load(self, ctx):
        super(ucommandsPlugin, self).load(ctx)

    @naPlugin.command("yttogether")
    def yttogether(self, event):
        state = event.guild.get_member(event.author).get_voice_state()
        if not state:
            return event.msg.reply('You must be connected to voice to use that command.')

        r = self.client.api.http(Routes.CHANNELS_INVITES_CREATE, dict(channel=state.channel.id),
                                 json={'max_age': 0, 'max_uses': 2, 'target_type': 2, 'target_application_id': Getcfgvalue("options.ucommands.wtid", "")})
        invite = Invite.create(self.client, r.json())
        return event.msg.reply(f"https://discord.gg/{invite.code}")
