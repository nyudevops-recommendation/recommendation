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

Scenario: Create a Recommendation
When I visit the "Home Page"
And I set the "Product_ID" to "4"
And I set the "Customer_ID" to "4"
And I set the "Recommend_Product_ID" to "6"
And I select "Upsell" in the "Recommend_Type" dropdown
And I press the "Create" button
Then I should see the message "Success"
When I copy the "Recommendation_ID" field
And I press the "Clear" button
Then the "Recommendation_Id" field should be empty
And the "Product_ID" field should be empty
And the "Customer_ID" field should be empty
And the "Recommend_Product_ID" field should be empty
When I paste the "Recommendation_ID" field
And I press the "Retrieve" button
Then I should see "4" in the "Product_ID" field
And I should see "4" in the "Customer_ID" field
And I should see "6" in the "Recommend_Product_ID" field
And I should see "Upsell" in the "Recommend_Type" dropdown
