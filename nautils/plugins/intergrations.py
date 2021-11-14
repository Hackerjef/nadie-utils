from flask import request, jsonify, abort
from nautils import naPlugin
from nautils.config import Getcfgvalue
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


class IntergrationPlugin(naPlugin):
    def load(self, ctx):
        self.vkey = VerifyKey(bytes.fromhex(Getcfgvalue("web.application_pkey", None)))
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



        #do shit
        if request.json["type"] == 1:
            return jsonify({
                "type": 1
            })
