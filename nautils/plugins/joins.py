from nautils import naPlugin
from nautils.config import Getcfgvalue


class joinPlugin(naPlugin):
    def load(self, ctx):
        super(joinPlugin, self).load(ctx)
        # todo: go through member list and yeet people out

    @naPlugin.listen('GuildMemberAdd')
    def joins_onjoin(self, event):
        if not Getcfgvalue("options.joins.enabled", False):
            return
        if event.id in Getcfgvalue("options.joins.soft_banned", []):
            # Fuck your nan
            event.kick(reason=f"{event.id} - User has been soft banned :)")
