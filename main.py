from flask import Flask, jsonify
from flask_restful import reqparse, Resource, Api

app = Flask(__name__)
api = Api(app)


class WizTask(Resource):
    def post(self):
        try:
            data = request.get_json()  
            if not data:
                return {'message': 'No data provided'}, 400
            
            # This is where we post it to a queue or similar
            processed_data = ""
            
            return {'processed_data': processed_data}, 200
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(WizTask, '/addTask')


if __name__ == "__main__":
    app.run()



# This is the "token" i am using for auth as of now
# 05cc0e19e80cc9d9742fbd3f9195a8de60837d6e085ed8e6b3c0501811b755e2