from flask import Flask, jsonify, request
from flask_restful import reqparse, Resource, Api
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import logging
# Imports the Cloud Logging client library
import google.cloud.logging
from google.cloud import pubsub_v1
import json
import functools

app = Flask(__name__)
api = Api(app)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/jarand/.config/gcloud/application_default_credentials.json"
os.environ["GCLOUD_PROJECT"] = "o3c-jarand-sandbox"
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

def validate_token(audience):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'error': 'Unauthorized'}, 401
            
            token = auth_header.split('Bearer ')[1]
            
            try:
                # Verify the token
                id_info = id_token.verify_oauth2_token(
                    token, 
                    requests.Request(), 
                    audience=audience
                )
                
                # Get the service account email that made the request
                caller_service_account = id_info.get('email')
                
                # Optionally check if this is the expected service account
                expected_service_account = '992741267002-compute@developer.gserviceaccount.com'
                if caller_service_account != expected_service_account:
                    return {'error': 'Unauthorized service account'}, 403
                
                # Add the verified identity to the request context
                request.caller_identity = id_info
                
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Token validation error: {e}")
                return {'error': 'Invalid token'}, 401
        return wrapper
    return decorator

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


@app.route('/case', methods=['POST'])
def wiz_task():
    my_var = os.getenv("AUTH_TOKEN")
    # Sjekk autentisering
    if request.headers.get('Authorization') ==  "Bearer {0}".format(my_var):
        logging.info("Authorization successful")
    else:
        logging.info("Authorization failed")
        return {'error': 'Unauthorized'}, 401
    
    try:
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

@app.route('/customercase', methods=['POST'])
@validate_token(audience='https://api-for-hackathon-918861751473.europe-north2.run.app')
def customer_case():
    # Access the caller identity if needed
    caller = request.caller_identity
    logging.info(f" User logged inn: {data}")
    try:
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


@app.route('/test', methods=['GET'])
@validate_token(audience='https://api-for-hackathon-918861751473.europe-north2.run.app')
def test():
    # Access the caller identity if needed
    return "You have been authorized", 200

@app.route('/wizupdate', methods=['POST'])
def wiz_update():
    my_var = os.getenv("AUTH_TOKEN")
    if request.headers.get('Authorization') ==  "Bearer {0}".format(my_var):
        logging.info("Authorization successful")
    else:
        logging.info("Authorization failed")
        return {'error': 'Unauthorized'}, 401
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        logging.info(f"Received Wiz data: {data}")
        success = publish_to_pubsub(data, "wiz-update")
        
        if success:
            return jsonify({'message': 'Data received and published to Pub/Sub'}), 200
        else:
            return jsonify({'error': 'Failed to publish to Pub/Sub'}), 500
        
    except Exception as e:
        logging.exception("Exception in WizTask")
        return {'error': str(e)}, 500


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    app.run()