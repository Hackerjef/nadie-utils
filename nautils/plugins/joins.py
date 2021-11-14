import gevent

from nautils import naPlugin
from nautils.config import Getcfgvalue


class joinPlugin(naPlugin):
    def load(self, ctx):
        super(joinPlugin, self).load(ctx)

    @naPlugin.listen("Ready")
    def joins_ready(self, event):
        gid = Getcfgvalue("options.gid", None)
        if gid:
            has_ran = False
            while not has_ran:
                g = self.bot.client.state.guilds.get(gid)
                if g:
                    for mid in list(g.members):
                        if mid not in Getcfgvalue("options.joins.soft_banned", []):
                            res = f"{mid} - User has been soft banned :) - bot startup"
                            self.log.info(res)
                            try:
                                #g.kick(mid, reason=res)
                                pass
                            except:
                                self.log.info(f"Can't kick user - {mid}")
                    has_ran = True
                else:
                    self.log.error("Guild not found for joins, sleeping 15")
                    gevent.sleep(15)

    @naPlugin.listen('GuildMemberAdd')
    def joins_onjoin(self, event):
        if not Getcfgvalue("options.joins.enabled", False):
            return

        if event.guild.id != Getcfgvalue("options.gid", None):
            return

        if event.id in Getcfgvalue("options.joins.soft_banned", []):
            # Fuck your nan
            event.kick(reason=f"{event.id} - User has been soft banned :)")
