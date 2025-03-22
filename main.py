from flask import Flask, jsonify, request
from flask_restful import reqparse, Resource, Api
import os
import logging

app = Flask(__name__)
api = Api(app)


class WizTask(Resource):
    def post(self):
        my_var = os.getenv("AUTH_TOKEN")
        try:
            # Sjekk autentisering
            if request.headers.get('Authorization') ==  my_var:

                data = request.get_json() 
                if not data:
                    return {'message': 'No data provided'}, 400

                logging.info(data)
                # tenant_id = Grab tenant id from auth token  
                # add tenant id to json object received from customer
                
                return {'processed_data': data}, 200
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(WizTask, '/case')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    app.run()