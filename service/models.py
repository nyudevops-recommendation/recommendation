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
type (string) - the type of the recommendation (upscale, downscale, etc)
recommend_product_id (int) - the identity of recommended product
"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
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

    def __init__(self):
        self.id = db.Column(db.Integer, primary_key=True)
        self.product_id = db.Column(db.Integer)
        self.customer_id = db.Column(db.Integer)
        self.type = db.Column(db.String(63))
        self.recommend_product_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Recommendation %r>' % self.id

    def save(self):
        """
        Saves a Recommendation to the data store
        """
        Recommendation.logger.info('Saving %s', self.name)
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        Recommendation.logger.info('Deleting %s', self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {"id": self.id,
                "product id": self.product_id,
                "customer id": self.customer_id,
                "type": self.type,
                "recommend id": self.recommend_product_id}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the Recommendation data
        """
        try:
            self.id = data['id']
            self.customer_id = data['customer_id']
            self.product_id = data['product_id']
            self.type = data['type']
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
    def find_or_404(cls,rec_id):
        """ Find a Recommendation by it's id """
        cls.logger.info('Processing lookup or 404 for id %s ...', rec_id)
        return cls.query.get_or_404(rec_id)

    @classmethod
    def find_by_product_id(cls, product_id):
        """ Returns all Recommendations with the given product id

        Args:
            product_id (string): the product id of the Recommendations you want to match
        """
        cls.logger.info('Processing product id query for %s ...', product_id)
        return cls.query.filter(cls.product_id == product_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """ Returns all of the Recommendations for a customer

        Args:
            customer_id (string): the customer id of the Recommendations you want to match
        """
        cls.logger.info('Processing customer id query for %s ...', customer_id)
        return cls.query.filter(cls.customer_id == customer_id)

    @classmethod
    def find_by_type(cls, type):
        """ Query that finds Recommendations by their type """
        """ Returns all Recommendations by their type

        Args:
            type (string): True for Recommendations that are available
        """
        cls.logger.info('Processing available query for %s ...', type)
        return cls.query.filter(cls.type == type)

    @classmethod
    def find_by_recommend_product_id(cls, recommend_product_id):
        """ Query that finds Recommendations by their recommend id """
        """ Returns all Recommendations by their recommend id

        Args:
            recommend_product_id (string): True for Recommendations that are available
        """
        cls.logger.info('Processing available query for %s ...', recommend_product_id)
        return cls.query.filter(cls.recommend_product_id == recommend_product_id)