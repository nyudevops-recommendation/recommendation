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
    return jsonify(name='Recommendation ',
                   version='1.0',
                   paths=url_for('list_recommendations', _external=True)
                  ), status.HTTP_200_OK
#
# ######################################################################
# # LIST ALL PETS
# ######################################################################
# @app.route('/recommendations', methods=['GET'])
# def list_recommendations():
#     """ Returns all of the Pets """
#     app.logger.info('Request for pet list')
#     pets = []
#     category = request.args.get('category')
#     name = request.args.get('name')
#     if category:
#         pets = Recommendation.find_by_category(category)
#     elif name:
#         pets = Recommendation.find_by_name(name)
#     else:
#         pets = Recommendation.all()
#
#     results = [pet.serialize() for pet in pets]
#     return make_response(jsonify(results), status.HTTP_200_OK)


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
    recommendation.save()
    message = recommendation.serialize()
    location_url = url_for('get_recommendations', rec_id=recommendation.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })
#
#
# ######################################################################
# # UPDATE AN EXISTING PET
# ######################################################################
# @app.route('/pets/<int:pet_id>', methods=['PUT'])
# def update_pets(pet_id):
#     """
#     Update a Recommendation
#
#     This endpoint will update a Recommendation based the body that is posted
#     """
#     app.logger.info('Request to update pet with id: %s', pet_id)
#     check_content_type('application/json')
#     pet = Recommendation.find(pet_id)
#     if not pet:
#         raise NotFound("Recommendation with id '{}' was not found.".format(pet_id))
#     pet.deserialize(request.get_json())
#     pet.id = pet_id
#     pet.save()
#     return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)
#
#
# ######################################################################
# # DELETE A PET
# ######################################################################
# @app.route('/pets/<int:pet_id>', methods=['DELETE'])
# def delete_pets(pet_id):
#     """
#     Delete a Recommendation
#
#     This endpoint will delete a Recommendation based the id specified in the path
#     """
#     app.logger.info('Request to delete pet with id: %s', pet_id)
#     pet = Recommendation.find(pet_id)
#     if pet:
#         pet.delete()
#     return make_response('', status.HTTP_204_NO_CONTENT)

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
