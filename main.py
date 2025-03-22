from flask import Flask, jsonify, request
from flask_restful import reqparse, Resource, Api
import os
import logging
# Imports the Cloud Logging client library
import google.cloud.logging
from google.cloud import pubsub_v1
import json

app = Flask(__name__)
api = Api(app)

# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.setup_logging()

# Pub/Sub config
PROJECT_ID = "o3c-jarand-sandbox"

publisher = pubsub_v1.PublisherClient()


def publish_to_pubsub(data, topic_id):
    """Publiserer JSON-data til Google Cloud Pub/Sub."""
    topic_path = publisher.topic_path(PROJECT_ID, topic_id)
    try:
        message_bytes = json.dumps(data).encode("utf-8")
        future = publisher.publish(topic_path, data=message_bytes)
        logging.info(f"Published message ID: {future.result()}")
        return True
    except Exception as e:
        logging.error(f"Failed to publish to Pub/Sub: {e}")
        return False

class WizTask(Resource):
    def post(self):
        my_var = os.getenv("AUTH_TOKEN")
        try:
            # Sjekk autentisering
            if request.headers.get('Authorization') ==  "Bearer {0}".format(my_var):
                logging.info("Authorization successful")
            else:
                logging.info("Authorization failed")
                return {'error': 'Unauthorized'}, 401

            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            logging.info(f" Received Wiz data: {data}")

            success = publish_to_pubsub(data, "wiz-issue")
            if success:
                return {'message': 'Data received and published to Pub/Sub'}, 200
            else:
                return {'error': 'Failed to publish to Pub/Sub'}, 500

        except Exception as e:
            logging.exception("Exception in WizTask")
            return {'error': str(e)}, 500


class WizUpdate(Resource):
    def post(self):
        my_var = os.getenv("AUTH_TOKEN")
        try:
            # Sjekk autentisering
            if request.headers.get('Authorization') ==  "Bearer {0}".format(my_var):
                logging.info("Authorization successful")
            else:
                logging.info("Authorization failed")
                return {'error': 'Unauthorized'}, 401

            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            logging.info(f" Received Wiz data: {data}")

            success = publish_to_pubsub(data, "wiz-update")
            if success:
                return {'message': 'Data received and published to Pub/Sub'}, 200
            else:
                return {'error': 'Failed to publish to Pub/Sub'}, 500

        except Exception as e:
            logging.exception("Exception in WizTask")
            return {'error': str(e)}, 500

api.add_resource(WizTask, '/case')
api.add_resource(WizUpdate, '/wizupdate')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    app.run()