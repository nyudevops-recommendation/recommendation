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
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    recommend_type = db.Column(db.String(63))
    recommend_product_id = db.Column(db.Integer)

    def save(self):
        """
        Saves a Recommendation to the data store
        """
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
                "product id": self.product_id,
                "customer id": self.customer_id,
                "recommend type": self.recommend_type,
                "recommend product id": self.recommend_product_id}

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
            self.recommend_type = data['recommend_type']
            self.recommend_product_id = data['recommend_product_id']
        except KeyError as error:
            raise DataValidationError('Invalid Recommendation: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Recommendation: body of request contained'
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
    def find_by_id(cls, id):
        """ Returns all of the Recommendation in an id
        Args:
            id (string): the id of the Recommendation you want to match
        """
        cls.logger.info('Processing id query for %s ...', id)
        return cls.query.filter(cls.id == id)
