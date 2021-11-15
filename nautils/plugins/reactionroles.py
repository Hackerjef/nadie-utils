import re

import gevent

from nautils import naPlugin
from nautils.config import Getcfgvalue

emoji_re = re.compile(r'<a?:(.+):([0-9]+)>')


class ReactionRolesPlugin(naPlugin):
    def load(self, ctx):
        super(ReactionRolesPlugin, self).load(ctx)
        if not Getcfgvalue("options.reaction_roles", None):
            self.log.info("Config not avaliable, not even trying to start")
            self.unload(ctx)

    def check_reactions(self):
        reactionrolescfg = Getcfgvalue("options.reaction_roles", [])
        self.log.info(reactionrolescfg)
        if not reactionrolescfg:
            return

        for mid in reactionrolescfg:
            rcfg = reactionrolescfg.get(mid, None)
            hasnt_ran = True
            while hasnt_ran:
                c = self.bot.client.state.channels.get(rcfg.get("cid", None), None)
                if c:
                    hasnt_ran = False
                    msg = c.get_message(mid)
                    if msg:
                        for reaction in rcfg.get("reactions", []):
                            emoji = emoji_re.findall(reaction)[0]
                            rid = int(emoji[1])
                            dformat = f"{str(emoji[0])}:{rid}"
                            rc = next(x for x in msg.reactions if x.emoji.id == rid)
                            if rc:
                                if not rc.me:
                                    msg.add_reaction(dformat)
                            else:
                                msg.add_reaction(dformat)
                    else:
                        self.log.warn(f"{mid} doesn't exist :)")
                else:
                    self.log.info("Channel not found in state yet, waiting")
                    gevent.sleep(1)
        self.log.info("Finnished illiteration of reaction roles on startup")

    @naPlugin.listen("Ready")
    def rr_ready(self, event):
        self.check_reactions()

    @naPlugin.listen("MessageReactionAdd")
    def rr_add(self, event):
        if event.user_id == self.client.state.me.id:
            return
        cfg = Getcfgvalue("options.reaction_roles", []).get(event.message_id, None)
        if not cfg:
            return
        rid = cfg.get("reactions", {}).get(f"<{'a' if event.emoji.animated else ''}:{event.emoji.name}:{event.emoji.id}>", None)
        if not rid:
            return
        event.guild.get_member(event.user_id).add_role(role=rid, reason="Reaction role")

    @naPlugin.listen("MessageReactionRemove")
    def rr_rmv(self, event):
        if event.user_id == self.client.state.me.id:
            return
        cfg = Getcfgvalue("options.reaction_roles", []).get(event.message_id, None)
        if not cfg:
            return
        rid = cfg.get("reactions", {}).get(f"<{'a' if event.emoji.animated else ''}:{event.emoji.name}:{event.emoji.id}>", None)
        if not rid:
            return
        event.guild.get_member(event.user_id).remove_role(role=rid, reason="Reaction role")
