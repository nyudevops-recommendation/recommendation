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


## To run the Flask app 

```
vagrant up
vagrant ssh
cd /vagrant
nosetests
FLASK_APP=service:app flask run --host=0.0.0.0 --port=5000
```
then on your own machine, visit: http://localhost:5000/

## To send out pull requests

```
git checkout -b my-branch
```
(add/modify something)
```
git add something
git commit -m "add/modify something"
```
(Tips: save your local changes to a safe place and pray for no merge conflicts would occur before you do the following...)  
```
git checkout master
git pull
git checkout my-branch
git merge master
```
(fix merge conflicts and git add, git commit again)
```
git push -u origin my-branch
```
(go to the PR page and attach your nosetests results in the description, and if there's no test results, the PR shouldn't be approved)

