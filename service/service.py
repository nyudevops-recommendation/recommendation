# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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

"""
Recommendation Service

Paths:
------
list: HTTP GET /recommendations - return a list all of the recommendations
read: HTTP GET /recommendations/{rec-id} - return the recommendation with id number
query: HTTP GET /recommendations?product-id=123&type=upscale&customer-id=111 return the recommendation with specific product-id, customer-id
create: HTTP POST /recommendations - creates a new recommendation record in the database
update: HTTP PUT /recommendations/{rec-id} - updates a recommendation record in the database
delete: HTTP DELETE /recommendations/{rec-id} - deletes a recommendation record in the database
success: HTTP PUT /recommendations/{rec-id}/success
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Recommendation, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                   error='Unsupported media type',
                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Recommendation Demo REST API Service',
                   version='1.0',
                   paths=url_for('list_recommendations', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL Recommendations
# HTTP GET /recommendations - return a list all of the recommendations
######################################################################
@app.route('/recommendations', methods=['GET'])
def list_recommendations():
    """ Returns all of the recommendations """
    app.logger.info('Request for recommendations list')
    recommendations = []
    product_id = request.args.get('product_id')
    customer_id = request.args.get('customer_id')
    recommend_type = request.args.get('recommend_type')
    if product_id:
        recommendations = Recommendation.find_by_product_id(product_id)
    elif customer_id:
        recommendations = Recommendation.find_by_customer_id(customer_id)
    elif recommend_type:
        recommendations = Recommendation.find_by_recommend_type(recommend_type)
    else:
        recommendations = Recommendation.all()

    results = [recommendations.serialize() for recommendation in recommendations]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A Recommendation
# HTTP GET /recommendations/{rec_id} - return the recommendation with id number
######################################################################
@app.route('/recommendations/<int:rec_id>', methods=['GET'])
def get_recommendations(rec_id):
    """
    Retrieve a single recommendation

    This endpoint will return a recommendation based on it's id
    """
    app.logger.info('Request for recommendation with id: %s', rec_id)
    recommendation = Recommendation.find(rec_id)
    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(rec_id))
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW Recommendation
# HTTP POST /recommendations - creates a new recommendation record in the database
######################################################################
@app.route('/recommendations', methods=['POST'])
def create_recommendations():
    """
    Creates a recommendation
    This endpoint will create a recommendation based the data in the body that is posted
    """
    app.logger.info('Request to create a recommendation')
    check_content_type('application/json')
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.save()
    message = recommendation.serialize()
    location_url = url_for('get_recommendations', recommendation_id=recommendation.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
# DELETE A recommendation
# HTTP DELETE /recommendations/{rec_id} - deletes a recommendation record in the database
######################################################################

@app.route('/pets/<int:rec_id>', methods=['DELETE'])
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