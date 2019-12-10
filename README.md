# Recommendations

[![Build Status](https://travis-ci.org/nyudevops-recommendation/recommendations.svg?branch=master)](https://travis-ci.org/nyudevops-recommendation/recommendations)
[![codecov](https://codecov.io/gh/nyudevops-recommendation/recommendations/branch/master/graph/badge.svg)](https://codecov.io/gh/nyudevops-recommendation/recommendations)


## Description

The recommendations resource is a representation a product recommendation based on another product. In essence it is just a relationship between two products that "go together" (e.g., radio and batteries, printers and ink, shirts and pants, etc.). It could also recommend based on what other customers have purchased like "customers who bought item A usually buy item B". Recommendations should have a recommendation type like cross-sell, upsell, accessory, etc. This way a product page could request all of the up-sells for a product.   

## API routes
- **root:** HTTP GET /
- **list:** HTTP GET /recommendations
- **query:** HTTP GET /recommendations?product-id={product_id}&customer-id={customer_id}&recommend-type={recommend_type}
- **read:** HTTP GET /recommendations/{id}
- **create:** HTTP POST /recommendations 
- **update:** HTTP PUT /recommendations/{id}
- **delete:** HTTP DELETE /recommendations/{id}
- **success:** HTTP PUT /recommendations/{id}/success
- **swagger API doc:** HTTP GET /apidocs


## Application URL: (deployed on IBM Cloud) 
dev link: https://nyu-recommendation-service-f19.mybluemix.net/   

prod link: https://nyu-recommendation-service-fa19.mybluemix.net/   

## CI/CD Pipeline URL: 
https://cloud.ibm.com/devops/pipelines/9b0d5bad-8e9f-4aae-83c8-dd2d02a415c8?env_id=ibm:yp:us-east


## To run the Flask app 

```
vagrant up
vagrant ssh
cd /vagrant
honcho start
```
then on your own machine, visit: http://localhost:5000/
