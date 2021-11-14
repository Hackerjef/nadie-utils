from nautils import naPlugin
from nautils.config import Getcfgvalue


def check_guild(g):
    for m in list(g.members):
        print(m)
        # if m in Getcfgvalue("options.joins.soft_banned", []):




class joinPlugin(naPlugin):
    def load(self, ctx):
        super(joinPlugin, self).load(ctx)

    @naPlugin.listen("Ready")
    def joins_ready(self, event):
        g = Getcfgvalue("options.gid", None)
        self.log.info(self.bot.client.state.guilds)

    @naPlugin.listen('GuildMemberAdd')
    def joins_onjoin(self, event):
        if not Getcfgvalue("options.joins.enabled", False):
            return

        if event.guild.id != Getcfgvalue("options.gid", None):
            return

        if event.id in Getcfgvalue("options.joins.soft_banned", []):
            # Fuck your nan
            event.kick(reason=f"{event.id} - User has been soft banned :)")
