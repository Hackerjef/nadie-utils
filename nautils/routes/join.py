import requests
from flask import Blueprint, session, redirect, request
from requests_oauthlib import OAuth2Session

from nautils.config import Getcfgvalue

join = Blueprint('join', __name__, url_prefix='/join')


def token_updater(token):
    pass


def make_discord_session_join(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=Getcfgvalue("discord.client_id", None),
        token=token,
        state=state,
        scope=scope,
        redirect_uri=Getcfgvalue("discord.redirects.join", None),
        auto_refresh_kwargs={
            'client_id': Getcfgvalue("discord.client_id", None),
            'client_secret': Getcfgvalue("discord.client_secret", None),
        },
        auto_refresh_url=Getcfgvalue("discord.oauth.token", None),
        token_updater=token_updater)


@join.route('/')
def auth_discord():
    if not Getcfgvalue("options.joins.enabled", False):
        return redirect(Getcfgvalue("options.joins.invite", "https://nadie.dev"))

    discord = make_discord_session_join(scope=('identify',))
    auth_url, state = discord.authorization_url(Getcfgvalue("discord.oauth.authorize", None))
    session['state'] = state
    return redirect(auth_url)


@join.route('/callback')
def auth_discord_callback():
    if request.values.get('error'):
        return 'An error has occurred', 418

    if 'state' not in session:
        return 'no state', 400

    discord = make_discord_session_join(state=session['state'])

    token = discord.fetch_token(
        Getcfgvalue("discord.oauth.token", None),
        client_secret=Getcfgvalue("discord.client_secret", None),
        authorization_response=request.url)

    discord = make_discord_session_join(token=token)

    user_data = discord.get(Getcfgvalue("discord.base_url", None) + '/users/@me').json()

    lsession = requests.Session()
    lsession.headers.update({'content-type': 'application/x-www-form-urlencoded'})
    lsession.post(Getcfgvalue("discord.oauth.revoke", None),
                  data={
                      'client_id': Getcfgvalue("discord.client_id", None),
                      'client_secret': Getcfgvalue("discord.client_secret", None),
                      'token': session['state']})

    if user_data['id'] in Getcfgvalue("options.joins.soft_banned", []):
        return redirect("https://youtu.be/LDU_Txk06tM?t=75")
    else:
        return redirect(Getcfgvalue("options.joins.invite", "https://nadie.dev"))
