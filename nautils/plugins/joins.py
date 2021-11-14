import gevent
import requests
from flask import session, redirect, request, send_file
from gevent import os
from oauthlib.oauth2 import MismatchingStateError
from requests_oauthlib import OAuth2Session

from nautils import naPlugin
from nautils.config import Getcfgvalue


def token_updater(token):
    pass


def make_discord_session_join(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=str(Getcfgvalue("discord.client_id", None)),
        token=token,
        state=state,
        scope=scope,
        redirect_uri=Getcfgvalue("discord.redirects.join", None),
        auto_refresh_kwargs={
            'client_id': str(Getcfgvalue("discord.client_id", None)),
            'client_secret': Getcfgvalue("discord.client_secret", None),
        },
        auto_refresh_url=Getcfgvalue("discord.oauth.token", None),
        token_updater=token_updater)


class joinPlugin(naPlugin):
    def load(self, ctx):
        super(joinPlugin, self).load(ctx)

    @naPlugin.listen("Ready")
    def joins_ready(self, event):
        self.hasnt_ran = True
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

    @naPlugin.route('/join', strict_slashes=False)
    def auth_discord(self):
        if "discord" in str(request.headers.get('User-Agent')).lower():
            return send_file(os.getcwd() + '/nautils/www/djoin.html')

        if not Getcfgvalue("options.joins.enabled", False):
            return redirect(Getcfgvalue("options.joins.invite", "https://nadie.dev"))

        discord = make_discord_session_join(scope=('identify', 'guilds.join'))
        auth_url, state = discord.authorization_url(Getcfgvalue("discord.oauth.authorize", None))
        session['state'] = state
        return redirect(auth_url)

    @naPlugin.route('/join/callback')
    def auth_discord_callback(self):
        if request.values.get('error'):
            if "acesss" in request.values.get('error').lower():
                return "You denied access through oauth, if you want to join the server just dm nadie :bongo:", 200
            else:
                return redirect("https://youtu.be/LDU_Txk06tM?t=75")

        if 'state' not in session:
            return 'no state', 400

        discord = make_discord_session_join(state=session['state'])

        try:
            token = discord.fetch_token(
                Getcfgvalue("discord.oauth.token", None),
                client_secret=Getcfgvalue("discord.client_secret", None),
                authorization_response=request.url)
        except MismatchingStateError:
            return redirect("/join")

        discord = make_discord_session_join(token=token)

        user_data = discord.get(Getcfgvalue("discord.base_url", None) + '/users/@me').json()

        if int(user_data['id']) in Getcfgvalue("options.joins.soft_banned", []):
            return redirect("https://youtu.be/LDU_Txk06tM?t=75")
        else:
            try:
                self.bot.client.api.guilds_members_add(Getcfgvalue("options.gid", None), user_data['id'],
                                                       token['access_token'])
                e = False
            except:
                e = True
            # return redirect(Getcfgvalue("options.joins.invite", "https://nadie.dev"))

        discord = None
        token = None
        lsession = requests.Session()
        lsession.headers.update({'content-type': 'application/x-www-form-urlencoded'})
        lsession.post(Getcfgvalue("discord.oauth.revoke", None),
                      data={
                          'client_id': str(Getcfgvalue("discord.client_id", None)),
                          'client_secret': Getcfgvalue("discord.client_secret", None),
                          'token': session['state']})

        if e:
            return "Discord didn't like me joining you to the guild, prob perms :)", 413
        else:
            return "You have been added to the guild enjoy", 200
