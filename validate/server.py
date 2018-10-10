"""Provide API for validating Translator Interchange API messages."""

import argparse
import yaml
import jsonschema
from flask import Flask, request, abort, Response
from flask_restful import Api, Resource
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)

api = Api(app)
CORS(app)

filename = 'translator_interchange.yaml'
with open(filename, 'r') as file_obj:
    template = yaml.load(file_obj)
app.config['SWAGGER'] = {
    'title': 'Translator Interchange API Specification',
    'uiversion': 3
}
swagger = Swagger(app, template=template)


class Validate(Resource):
    """Validate Translator Interchange API messages."""

    def post(self):
        """
        Validate the format of a message.
        ---
        tag: validation
        description: We're not actually doing anything with it.
        requestBody:
            description: Input message
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Message'
        responses:
            '200':
                description: Success
                content:
                    text/plain:
                        schema:
                            type: string
                            example: "Successfully validated"
            '400':
                description: Malformed message
                content:
                    text/plain:
                        schema:
                            type: string

        """
        with open(filename, 'r') as file_obj:
            specs = yaml.load(file_obj)
        to_validate = specs['definitions']['Message']
        to_validate['definitions'] = specs['definitions']
        to_validate['definitions'].pop('Message', None)
        try:
            jsonschema.validate(request.json, to_validate)
        except jsonschema.exceptions.ValidationError as error:
            abort(Response(str(error), 400))
        return "Successfully validated", 200

api.add_resource(Validate, '/validate')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-port', action="store", dest="port", default=80, type=int)
    args = parser.parse_args()

    server_host = '0.0.0.0'
    server_port = args.port

    app.run(
        host=server_host,
        port=server_port,
        debug=False,
        use_reloader=True
    )
