# Recommendations

## Description

The recommendations resource is a representation a product recommendation based on another product. In essence it is just a relationship between two products that "go together" (e.g., radio and batteries, printers and ink, shirts and pants, etc.). It could also recommend based on what other customers have purchased like "customers who bought item A usually buy item B". Recommendations should have a recommendation type like cross-sell, upsell, accessory, etc. This way a product page could request all of the up-sells for a product.   

## API routes

- **list:** HTTP GET /recommendations
- **read:** HTTP GET /recommendations/{rec-id}
- **query:** HTTP GET /recommendations?product-id=123&type=upscale&customer-id=111
- **create:** HTTP POST /recommendations 
- **update:** HTTP PUT /recommendations/{rec-id}
- **delete:** HTTP DELETE /recommendations/{rec-id}
- **success:** HTTP PUT /recommendations/{rec-id}/success


## To run the Flask app 

```
vagrant up
vagrant ssh
cd /vagrant
nosetests
FLASK_APP=service:app flask run --host=0.0.0.0 --port=5000
```
then on your own machine, visit: http://localhost:5000/
