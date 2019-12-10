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
Test cases for Recommendation Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Recommendation, DataValidationError, db
from service import app

#DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://postgres:passw0rd@localhost:5432/postgres')

#DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://soqerjpq:YZCacYhoNGHPtbX0zixiq7Lu81MrRJ1U@salt.db.elephantsql.com:5432/soqerjpq')
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://postgres:postgres@localhost:5432/postgres')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendations(unittest.TestCase):
    """ Test Cases for Recommendations """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_recommendation(self):
        """ Create a recommendation and assert that it exists """
        recommendation = Recommendation()
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.customer_id, None)
        self.assertEqual(recommendation.product_id, None)
        self.assertEqual(recommendation.recommend_product_id, None)
        self.assertEqual(recommendation.recommend_type, None)

    def test_add_a_recommendation(self):
        """ Create a recommendation and add it to the database """
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(customer_id=2,
                                        product_id=3, recommend_product_id=4,
                                        recommend_type="upsell")
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        recommendation.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(recommendation.id, 1)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)

    def test_update_a_recommendation(self):
        """ Update a Recommendation """
        recommendation = Recommendation(customer_id=2,
                                        product_id=3, recommend_product_id=4,
                                        recommend_type="upsell")
        recommendation.save()
        self.assertEqual(recommendation.id, 1)
        # Change it an save it
        recommendation.recommend_product_id = 5
        recommendation.save()
        self.assertEqual(recommendation.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].recommend_product_id, 5)

    def test_delete_a_recommendation(self):
        """ Delete a Recommendation """
        recommendation = Recommendation(customer_id=2,
                                        product_id=3, recommend_product_id=4,
                                        recommend_type="upsell")
        recommendation.save()
        self.assertEqual(len(Recommendation.all()), 1)
        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)
		
    def test_reset(self):
        """ Reset """
        recommendation = Recommendation(customer_id=2,
                                        product_id=3, recommend_product_id=4,
                                        recommend_type="upsell")
        recommendation.save()
        self.assertEqual(len(Recommendation.all()), 1)
        # delete the recommendation and make sure it isn't in the database
        recommendation.remove_all()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """
        recommendation = Recommendation(customer_id=2,
                                        product_id=3, recommend_product_id=4,
                                        recommend_type="upsell",
                                        rec_success=9)

        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('customer_id', data)
        self.assertEqual(data['customer_id'], 2)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], 3)
        self.assertIn('recommend_product_id', data)
        self.assertEqual(data['recommend_product_id'], 4)
        self.assertIn('recommend_type', data)
        self.assertEqual(data['recommend_type'], "upsell")
        self.assertIn('rec_success', data)
        self.assertEqual(data['rec_success'], 9)

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        data = {"id": 1, "customer_id": 2,\
         "product_id": 3, "recommend_product_id": 4, "recommend_type": "upsell"}
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.customer_id, 2)
        self.assertEqual(recommendation.product_id, 3)
        self.assertEqual(recommendation.recommend_product_id, 4)
        self.assertEqual(recommendation.recommend_type, "upsell")

    def test_deserialize_a_recommendation_negative_value(self):
        """ Test deserialization of a Recommendation with negative value """
        data = {"id": 1, "customer_id": -2,\
         "product_id": 3, "recommend_product_id": 4, "recommend_type": "upsell"}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_missing_data(self):
        """ Test deserialization of a Recommendation with missing data"""
        data = {"id": 1}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_no_data(self):
        """ Test deserialization of no data """
        data = None
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_find_recommendation(self):
        """ Find a Recommendation by ID """
        Recommendation(customer_id=2, product_id=3, recommend_product_id=4,\
        recommend_type="upsell").save()
        recc = Recommendation(customer_id=5, product_id=6,\
         recommend_product_id=7, recommend_type="downsell")
        recc.save()
        recommendation = Recommendation.find(recc.id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, recc.id)
        self.assertEqual(recommendation.product_id, 6)
        self.assertEqual(recommendation.customer_id, 5)

    def test_find_by_product_id(self):
        """ Find Recommendation by product_id """
        Recommendation(customer_id=2,
                       product_id=3, recommend_product_id=4,
                       recommend_type="upsell").save()
        Recommendation(customer_id=5,
                       product_id=6, recommend_product_id=7,
                       recommend_type="downsell").save()
        recommendations = Recommendation.find_by_product_id(6)
        self.assertEqual(recommendations[0].customer_id, 5)
        self.assertEqual(recommendations[0].product_id, 6)
        self.assertEqual(recommendations[0].recommend_product_id, 7)
        self.assertEqual(recommendations[0].recommend_type, "downsell")

    def test_find_by_customer_id(self):
        """ Find Recommendation by customer_id """
        Recommendation(customer_id=2,
                       product_id=3, recommend_product_id=4,
                       recommend_type="upsell").save()
        Recommendation(customer_id=5,
                       product_id=6, recommend_product_id=7,
                       recommend_type="downsell").save()
        recommendations = Recommendation.find_by_customer_id(5)
        self.assertEqual(recommendations[0].customer_id, 5)
        self.assertEqual(recommendations[0].product_id, 6)
        self.assertEqual(recommendations[0].recommend_product_id, 7)
        self.assertEqual(recommendations[0].recommend_type, "downsell")

    def test_find_by_recommend_type(self):
        """ Find Recommendation by recommend_type """
        Recommendation(customer_id=2,
                       product_id=3, recommend_product_id=4,
                       recommend_type="upsell").save()
        Recommendation(customer_id=5,
                       product_id=6, recommend_product_id=7,
                       recommend_type="downsell").save()
        recommendations = Recommendation.find_by_recommend_type("downsell")
        self.assertEqual(recommendations[0].customer_id, 5)
        self.assertEqual(recommendations[0].product_id, 6)
        self.assertEqual(recommendations[0].recommend_product_id, 7)
        self.assertEqual(recommendations[0].recommend_type, "downsell")

    def test_find_by_attributes(self):
        """ Find Recommendation by some attributes """
        Recommendation(customer_id=2,
                       product_id=3, recommend_product_id=4,
                       recommend_type="upsell").save()
        Recommendation(customer_id=2,
                       product_id=3, recommend_product_id=4,
                       recommend_type="downsell").save()
        Recommendation(customer_id=5,
                       product_id=6, recommend_product_id=7,
                       recommend_type="downsell").save()
        recommendations = Recommendation.find_by_attributes(3, 2, "downsell")
        self.assertEqual(recommendations[0].recommend_type, "downsell")
        self.assertEqual(recommendations[0].product_id, 3)
        self.assertEqual(recommendations[0].customer_id, 2)
        recommendations = Recommendation.find_by_attributes(3, 2, None)
        self.assertEqual(recommendations[0].recommend_type, "upsell")
        self.assertEqual(recommendations[0].product_id, 3)
        self.assertEqual(recommendations[0].customer_id, 2)
        self.assertEqual(recommendations[1].recommend_type, "downsell")
        self.assertEqual(recommendations[1].product_id, 3)
        self.assertEqual(recommendations[1].customer_id, 2)
