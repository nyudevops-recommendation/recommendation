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
Recommendation API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
from flask_api import status  # HTTP Status Codes
from unittest.mock import MagicMock, patch
from service.models import Recommendation, DataValidationError, db
from .recommendation_factory import RecommendationFactory
from service.service import app, init_db, initialize_logging

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://postgres:passw0rd@localhost:5432/postgres')


######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendationServer(unittest.TestCase):
    """ Recommendation Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        initialize_logging(logging.INFO)
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        init_db()
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_recommendations(self, count):
        """ Factory method to create recommendations in bulk """
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            resp = self.app.post('/recommendations',
                                 json=test_recommendation.serialize(),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create test recommendation')
            new_recommendation = resp.get_json()
            test_recommendation.id = new_recommendation['id']
            recommendations.append(test_recommendation)
        return recommendations

    def test_create_recommendation(self):
        """ Create a new Recommendation """
        test_recommendation = RecommendationFactory()
        resp = self.app.post('/recommendations',
                             json=test_recommendation.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_recommendation = resp.get_json()
        self.assertEqual(new_recommendation['product_id'], test_recommendation.product_id, "product_id do not match")
        self.assertEqual(new_recommendation['customer_id'], test_recommendation.customer_id, "customer_id do not match")
        self.assertEqual(new_recommendation['recommend_type'], test_recommendation.recommend_type,
                         "product_type does not match")
        self.assertEqual(new_recommendation['recommend_product_id'], test_recommendation.recommend_product_id,
                         "recommend_product_id does not match")

        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_recommendation = resp.get_json()
        self.assertEqual(new_recommendation['product_id'], test_recommendation.product_id, "product_id do not match")
        self.assertEqual(new_recommendation['customer_id'], test_recommendation.customer_id, "customer_id do not match")
        self.assertEqual(new_recommendation['recommend_type'], test_recommendation.recommend_type,
                         "product_type does not match")
        self.assertEqual(new_recommendation['recommend_product_id'], test_recommendation.recommend_product_id,
                         "recommend_product_id does not match")
