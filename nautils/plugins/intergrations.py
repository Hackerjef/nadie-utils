# This is not getting used because interactions makes me die :) AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

from disco.types.application import InteractionType,  Interaction
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
        signature, timestamp = None, None
        try:
            signature = request.headers["X-Signature-Ed25519"]
            timestamp = request.headers["X-Signature-Timestamp"]
        except:
            abort(400)
        body = request.data.decode("utf-8")

        try:
            self.vkey.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        except BadSignatureError:
            abort(401, 'invalid request signature')

        if request.json["type"] == InteractionType.PING:
            self.log.info("ping")
            self.log.info(body)
            return jsonify({"type": 1})
        elif request.json["type"] == InteractionType.APPLICATION_COMMAND:
            interaction = Interaction.create(client=self.bot.client, data=request.json)
            self.log.info("app command")
            self.log.info(interaction)
            return "ok", 200
        elif request.json['type'] == InteractionType.MessageComponent:
            interaction = Interaction.create(client=self.bot.client, data=request.json)
            self.log.info("msg component")
            self.log.info(interaction)
            return "ok", 200
        elif request.json['type'] == 4:
            self.log.info("..auto complete?")
            self.log.info(body)
            return "ok", 200
        else:
            abort(401, 'invalid type given')
