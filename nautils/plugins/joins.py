import gevent

from nautils import naPlugin
from nautils.config import Getcfgvalue


class joinPlugin(naPlugin):
    def load(self, ctx):
        super(joinPlugin, self).load(ctx)
        self.hasnt_ran = True

    @naPlugin.listen("Ready")
    def joins_ready(self, event):
        gid = Getcfgvalue("options.gid", None)
        if gid:
            while self.hasnt_ran:
                g = self.bot.client.state.guilds.get(gid)
                if g:
                    for mid in list(g.members):
                        if mid in Getcfgvalue("options.joins.soft_banned", []):
                            res = f"{mid} - User has been soft banned :) - bot startup"
                            self.log.info(res)
                            try:
                                self.client.api.guilds_members_kick(g.id, mid, reason=res)
                            except:
                                self.log.info(f"Can't kick user - {mid}")
                    self.hasnt_ran = False
                else:
                    self.log.error("Guild not found for joins, sleeping for 1s")
                    gevent.sleep(1)

    @naPlugin.listen('GuildMemberAdd')
    def joins_onjoin(self, event):
        if not Getcfgvalue("options.joins.enabled", False):
            return

        if event.guild.id != Getcfgvalue("options.gid", None):
            return

        if event.id in Getcfgvalue("options.joins.soft_banned", []):
            # Fuck your nan
            event.kick(reason=f"{event.id} - User has been soft banned :)")
