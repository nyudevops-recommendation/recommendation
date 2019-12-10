# Copyright 2016, 2019 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Recommendation Demo Service

All of the models are stored in this module

Models
------
Recommendation - A Recommendation used in the Recommendation Store

Attributes:
-----------
id (int) - the identity of the Recommendation
product_id (int) - the identity of the product that the recommendation is for
customer_id (int) - the identity of the customer that the recommendation is for
recommend_type (string) - the recommend_type of the recommendation (upscale, downscale, etc)
recommend_product_id (int) - the identity of recommended product
"""
import logging
import os
from flask_sqlalchemy import SQLAlchemy

# pylint: disable=no-member

# Create the SQLAlchemy object to be initialized later in init_db()
from requests import HTTPError

db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Recommendation(db.Model):
    """
    Class that represents a Recommendation

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger('flask.app')
    app = None

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    recommend_type = db.Column(db.String(63))
    recommend_product_id = db.Column(db.Integer)
    rec_success = db.Column(db.Integer)

    def save(self):
        """
        Saves a Recommendation to the data store
        """
        if self.product_id is None or self.customer_id is None \
                or self.recommend_type is None or self.recommend_product_id is None\
                or type(self.product_id) is not int or type(self.customer_id) is not int \
                or type(self.recommend_type) is not str or type(self.recommend_product_id) is not int :
            raise DataValidationError('invalid input.')
        Recommendation.logger.info('Saving %s', self.id)
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        Recommendation.logger.info('Deleting %s', self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {"id": self.id,
                "product_id": self.product_id,
                "customer_id": self.customer_id,
                "recommend_type": self.recommend_type,
                "recommend_product_id": self.recommend_product_id,
				"rec_success": self.rec_success}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the Recommendation data
        """
        try:
            self.product_id = data['product_id']
            self.customer_id = data['customer_id']
            self.recommend_type = data['recommend_type']
            self.recommend_product_id = data['recommend_product_id']
        except KeyError as error:
            raise DataValidationError('Invalid Recommendation: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Recommendation: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables
#        #Recommendation(customer_id=2,
#                       product_id=3,
#                       recommend_product_id=4,
#                       recommend_type="upsell",
#                       rec_success=0).save()
#        #Recommendation(customer_id=5,
#                       product_id=6,
#                       recommend_product_id=7,
#                       recommend_type="downsell",
#                       rec_success=2).save()
#        #Recommendation(customer_id=5,
#                       product_id=6,
#                       recommend_product_id=8,
#                       recommend_type="upsell",
#                       rec_success=1).save()

    @classmethod
    def all(cls):
        """ Returns all of the Recommendations in the database """
        cls.logger.info('Processing all Recommendations')
        return cls.query.all()

    @classmethod
    def find(cls, rec_id):
        """ Finds a Recommendation by it's ID """
        cls.logger.info('Processing lookup for id %s ...', rec_id)
        return cls.query.get(rec_id)

    @classmethod
    def find_by_product_id(cls, product_id):
        """ Returns all of the Recommendation in an product_id
        Args:
            product_id (string): the product_id of the Recommendation you want to match
        """
        cls.logger.info('Processing product_id query for %s ...', product_id)
        return cls.query.filter(cls.product_id == product_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """ Returns all of the Recommendation in an customer_id
        Args:
            customer_id (string): the customer_id of the Recommendation you want to match
        """
        cls.logger.info('Processing customer_id query for %s ...', customer_id)
        return cls.query.filter(cls.customer_id == customer_id)

    @classmethod
    def find_by_recommend_type(cls, recommend_type):
        """ Returns all of the Recommendation in an recommend_type
        Args:
            recommend_type (string): the recommend_type of the Recommendation you want to match
        """
        cls.logger.info('Processing recommend_type query for %s ...', recommend_type)
        return cls.query.filter(cls.recommend_type == recommend_type)

    @classmethod
    def find_by_attributes(cls, product_id, customer_id, recommend_type):
        """ Returns all of the Recommendation with specific attributes
        Args:
            :param recommend_type: query by recommend_type
            :param customer_id: query by customer_id
            :param product_id: query by product_id
        """
        cls.logger.info('Processing query for product_id: %s, '
                        'customer_id: %s, recommend_type: %s ...',
                        product_id, customer_id, recommend_type)
        result = cls.query
        if product_id:
            result = result.filter(cls.product_id == product_id)
        if customer_id:
            result = result.filter(cls.customer_id == customer_id)
        if recommend_type:
            result = result.filter(cls.recommend_type == recommend_type)
        return result.all()
		
    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        cls.query.delete();
