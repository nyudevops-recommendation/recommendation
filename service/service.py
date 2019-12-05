#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys
import logging
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from service.models import Recommendation

# Import Flask application
from service import app
from utils import errorHandlers
# pylint: disable=no-member

# Document the type of autorization required
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Api-Key'
    }
}

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return app.send_static_file('index.html')

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Recommendation REST API Service',
          description='This is Recommendation Microservice server.',
          default='recommendations',
          default_label='Recommendation operations',
          doc='/apidocs/',
          authorizations=authorizations
          # prefix='/api'
         )

# Define the model so that the docs reflect what can be sent
recommendation_model = api.model('Recommendation', {
    'id': fields.Integer(readOnly=True,
                         description='The unique id assigned internally by service'),
    'product_id': fields.Integer(required=True,
                          description='The id of the product'),
    'customer_id': fields.Integer(required=True,
                                 description='The id of the customer'),
    'recommend_type': fields.String(required=True,
                                  description='The recommendation type, e.g. up-sell, down-sell, etc.'),
    'recommend_product_id': fields.Integer(required=True,
                                  description='The id of the recommended product'),
    'rec_success': fields.Integer(required=True,
                                    description='Recommendation success count')
})

create_model = api.model('Recommendation', {
    'product_id': fields.Integer(required=True,
                                 description='The id of the product'),
    'customer_id': fields.Integer(required=True,
                                  description='The id of the customer'),
    'recommend_type': fields.String(required=True,
                                    description='The recommendation type, e.g. up-sell, down-sell, etc.'),
    'recommend_product_id': fields.Integer(required=True,
                                           description='The id of the recommended product'),
    'rec_success': fields.Integer(required=True,
                                  description='Recommendation success count')
})

# query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument('product_id', type=int, required=False, help='List Recommendations by product_id')
recommendation_args.add_argument('customer_id', type=int, required=False, help='List Recommendations by customer_id')
recommendation_args.add_argument('recommend_type', type=str, required=False, help='List Recommendations by recommend type')

######################################################################
# LIST AND QUERY RECOMMENDATIONS
#  PATH: /recommendations
######################################################################
@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):
    """ Handles all interactions with collections of Recommendations """
    @api.doc('list_recommendations')
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """ List all or query the Recommendations"""
        app.logger.info('Request to list Recommendations...')
        product_id = request.args.get('product-id')
        customer_id = request.args.get('customer-id')
        recommend_type = request.args.get('recommend-type')
        recommendations = Recommendation.find_by_attributes(product_id, customer_id, recommend_type)
        if not recommendations:
            raise NotFound("Recommendation with product_id {}, "
                           "customer_id {}, recommend_type {} was not found."
                           .format(product_id, customer_id, recommend_type))
        results = [recommendation.serialize() for recommendation in recommendations]
        return results, status.HTTP_200_OK

# #####################################################################
# RETRIEVE A RECOMMENDATION
# #####################################################################
@app.route('/recommendations/<int:rec_id>', methods=['GET'])
def get_recommendations(rec_id):
    """
    Retrieve a single Recommendation
    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info('Request for recommendation with id: %s', rec_id)
    recommendation = Recommendation.find(rec_id)
    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(rec_id))
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW RECOMMENDATION
######################################################################
@app.route('/recommendations', methods=['POST'])
def create_recommendations():
    """
    Creates a Recommendation
    This endpoint will create a Recommendation based the data in the body that is posted
    """
    app.logger.info('Request to create a Recommendation')
    check_content_type('application/json')
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.rec_success = 0
    recommendation.save()
    message = recommendation.serialize()
    location_url = url_for('get_recommendations', rec_id=recommendation.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })


######################################################################
# DELETE A RECOMMENDATION
# HTTP DELETE /recommendations/{rec_id} - deletes a recommendation record in the database
######################################################################

@app.route('/recommendations/<int:rec_id>', methods=['DELETE'])
def delete_recommendations(rec_id):
    """
    Delete a recommendation

    This endpoint will delete a recommendation based the id specified in the path
    """
    app.logger.info('Request to delete recommendation with id: %s', rec_id)
    recommendation = Recommendation.find(rec_id)
    if recommendation:
        recommendation.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
# UPDATE AN EXISTING RECOMMENDATION
# HTTP PUT /recommendations/{rec_id} - updates a recommendation record in the database
######################################################################
@app.route('/recommendations/<int:rec_id>', methods=['PUT'])
def update_recommendations(rec_id):
    """
    Update a Recommendations
    This endpoint will update a Recommendation based the body that is posted
    """
    app.logger.info('Request to update recommendation with id: %s', rec_id)
    check_content_type('application/json')
    recommendation = Recommendation.find(rec_id)
    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(rec_id))
    recommendation.deserialize(request.get_json())
    recommendation.id = rec_id
    recommendation.save()
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)
	
######################################################################
# INCREMENT SUCCESS COUNTER
# HTTP PUT /recommendations/{rec_id} - increments the success counter of a given record
######################################################################
@app.route('/recommendations/<int:rec_id>/success', methods=['PUT'])
def rec_success(rec_id):
    """
    Increment A Recommendation's Success field
    """
    app.logger.info('Increment success field for recommendation with id: %s', rec_id)
    check_content_type('application/json')
    recommendation = Recommendation.find(rec_id)
    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(rec_id))
    count = recommendation.rec_success
    recommendation.rec_success = count + 1
    recommendation.id = rec_id
    recommendation.save()
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)
	
######################################################################
# DELETE ALL RECOMMENDATION DATA 
######################################################################
@app.route('/recommendations/reset', methods=['DELETE'])
def recommendations_reset():
    """ Removes all recommendations from the database """
    Recommendation.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Recommendation.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))


def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
        app.logger.info('Logging handler established')
