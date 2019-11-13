"""
Recommendation Steps

Steps file for Recommendation.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
from os import getenv
import logging
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))

@given('the following recommendations')
def step_impl(context):
    """ Delete all Recommendations and load new ones """
    headers = {'Content-Type': 'application/json'}
    #context.resp = requests.delete(context.base_url + '/recommendations/reset', headers=headers)
    #expect(context.resp.status_code).to_equal(204)
    create_url = context.base_url + '/recommendations'
    for row in context.table:
        data = {
            "product_id": row['product_id'],
            "customer_id": row['customer_id'],
            "recommend_type": row['recommend_type'],
            "recommend_product_id": row['recommend_product_id'],
            "rec_success": row['rec_success']
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    #context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)