Feature: The recommendation service back-end
    As a recommendation service Owner
    I need a RESTful catalog service
    So that I can keep track of all my recommendations

Background:
    Given the following recommendations
        | product_id | customer_id | recommend_type | recommend_product_id | rec_success |
        | 1          | 2           | upsell         | 3                    | 0           |
        | 1          | 2           | downsell       | 4                    | 2           |
        | 3          | 3           | accessory      | 1                    | 1           |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations Service DEMO" in the title
    And I should not see "404 Not Found"