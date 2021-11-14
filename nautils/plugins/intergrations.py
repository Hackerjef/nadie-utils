from disco.types.application import InteractionType, InteractionResponse, InteractionCallbackType
from flask import request, jsonify, abort
from nautils import naPlugin
from nautils.config import Getcfgvalue
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


class IntergrationPlugin(naPlugin):
    def load(self, ctx):
        self.vkey = VerifyKey(bytes.fromhex(Getcfgvalue("discord.application_pkey", None)))
        super(IntergrationPlugin, self).load(ctx)

    @naPlugin.route("/interactions", strict_slashes=False, methods=['POST'])
    def interactions(self):
        # Check security
        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]
        body = request.data.decode("utf-8")

        try:
            self.vkey.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        except BadSignatureError:
            abort(401, 'invalid request signature')

        if request.json["type"] == InteractionType.PING:
            return jsonify(InteractionResponse.create(type=InteractionCallbackType.PONG))
        elif request.json["type"] == InteractionType.APPLICATION_COMMAND:
            return self.app_command()
        elif request.json['type'] == InteractionType.MessageComponent:
            return self.msg_component()
        elif request.json['type'] == 4:
            return self.app_autocomplete()
        else:
            abort(401, 'invalid type given')

    def app_command(self):
        pass

    def app_autocomplete(self):
        pass

    def msg_component(self):
        pass