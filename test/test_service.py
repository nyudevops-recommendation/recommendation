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
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from service.models import Recommendation, DataValidationError, db
from service.service import app, init_db, initialize_logging
from .recommendation_factory import RecommendationFactory


# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
#DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://postgres:passw0rd@localhost:5432/postgres')
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://soqerjpq:YZCacYhoNGHPtbX0zixiq7Lu81MrRJ1U@salt.db.elephantsql.com:5432/soqerjpq')

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
        init_db()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b'Recommendations Service DEMO', resp.data)

    def _create_recommendations(self, count):
        """ Factory method to create recommendations in bulk """
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            resp = self.app.post('/recommendations',
                                 json=test_recommendation.serialize(),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED,
                             'Could not create test recommendation')
            new_recommendation = resp.get_json()
            test_recommendation.id = new_recommendation['id']
            recommendations.append(test_recommendation)
        return recommendations

    def test_get_recommendation_list(self):
        """ Get a list of Recommendations """
        self._create_recommendations(5)
        resp = self.app.get('/recommendations')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_recommendation(self):
        """ Get a single Recommendation """
        # get the id of a recommendation
        test_rec = self._create_recommendations(1)[0]
        resp = self.app.get('/recommendations/{}'.format(test_rec.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['id'], test_rec.id)

    def test_create_recommendation(self):
        """ Create a new Recommendation """
        test_recommendation = RecommendationFactory()
        resp = self.app.post('/recommendations',
                             json=test_recommendation.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location is not None)
        # Check the data is correct
        new_recommendation = resp.get_json()

        self.assertEqual(new_recommendation['product_id'],\
         test_recommendation.product_id, "product_id do not match")
        self.assertEqual(new_recommendation['customer_id'],\
         test_recommendation.customer_id, "customer_id do not match")
        self.assertEqual(new_recommendation['recommend_type'],\
         test_recommendation.recommend_type, "product_type does not match")
        self.assertEqual(new_recommendation['rec_success'],\
         test_recommendation.rec_success, "rec_success does not match")
        self.assertEqual(new_recommendation['recommend_product_id'],\
         test_recommendation.recommend_product_id, "recommend_product_id does not match")

        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_recommendation = resp.get_json()
        self.assertEqual(new_recommendation['product_id'],
                         test_recommendation.product_id, "product_id do not match")
        self.assertEqual(new_recommendation['customer_id'],
                         test_recommendation.customer_id, "customer_id do not match")
        self.assertEqual(new_recommendation['recommend_type'],
                         test_recommendation.recommend_type, "product_type does not match")
        self.assertEqual(new_recommendation['recommend_product_id'],
                         test_recommendation.recommend_product_id,
                         "recommend_product_id does not match")

    def test_create_recommendation_bad_content_type(self):
        """ Create a new Recommendation with bad content type """
        test_recommendation = RecommendationFactory()
        resp = self.app.post('/recommendations',
                             json=test_recommendation.serialize(),
                             content_type="a_bad_type")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_recommendation_not_found(self):
        """ Get a Recommendation thats not found """
        resp = self.app.get('/recommendations/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recommendation(self):
        """ Delete a Recommendation """
        test_recommendation = self._create_recommendations(1)[0]
        resp = self.app.delete('/recommendations/{}'.format(test_recommendation.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/recommendations/{}'.format(test_recommendation.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
		
    def test_reset(self):
        """ RESET """
        test_recommendation = self._create_recommendations(1)[0]
        resp = self.app.delete('/recommendations/reset',
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/recommendations/{}'.format(test_recommendation.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_recommendation(self):
        """ Update an existing Recommendation """
        # create a recommendation to update
        test_recommendation = RecommendationFactory()
        resp = self.app.post('/recommendations',
                             json=test_recommendation.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the recommendation
        test_recommendation = resp.get_json()
        test_recommendation['recommend_type'] = 'unknown'
        resp = self.app.put('/recommendations/{}'.format(test_recommendation['id']),
                            json=test_recommendation,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_recommendation = resp.get_json()
        self.assertEqual(updated_recommendation['recommend_type'], 'unknown')

    def test_success(self):
        """ Increment Success """
        # create a recommendation to increment
        test_recommendation = RecommendationFactory()
        resp = self.app.post('/recommendations',
                             json=test_recommendation.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # increment the recommendation
        new_recommendation = resp.get_json()
        resp = self.app.put('/recommendations/{}/success'.format(new_recommendation['id']),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_recommendation = resp.get_json()
        self.assertEqual(updated_recommendation['rec_success'], 1)

    def test_success_not_found(self):
        """ Increment Success with bad id """
        test_recommendation = RecommendationFactory()
        resp = self.app.put('/recommendations/0/success',
                            json=test_recommendation.serialize(),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_recommendation_not_found(self):
        """ Update a Recommendation thats not found """
        test_recommendation = RecommendationFactory()
        resp = self.app.put('/recommendations/0',
                            json=test_recommendation.serialize(),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_recommendation(self):
        """ Query by customer_id and product_id """
        test_rec = self._create_recommendations(5)[0]
        resp = self.app.get('/recommendations?product-id={}&customer-id={}'\
        .format(test_rec.product_id, test_rec.customer_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()[0]
        self.assertEqual(data['recommend_type'], test_rec.recommend_type)

    def test_query_recommendation_multiple_entries(self):
        """ Query by an specific recommend_type return multiple entries"""
        self._create_recommendations(10)
        resp = self.app.get('/recommendations?recommend-type={}'.format("upsell"))
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(data), 0)

    def test_query_recommendation_not_found(self):
        """ Query by an non-exist recommend_type """
        self._create_recommendations(5)
        resp = self.app.get('/recommendations?recommend-type={}'.format("a_strange_type"))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
