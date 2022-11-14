# Voucher API

## problem definition
we need a voucher API to get the best voucher for each customer based on its segment.
We have historical voucher data of customers, and by doing customer segmentation on them, we can decide which voucher 
is best for each customer segment. Next, we can recommend a voucher for a new customer based on its segment.

## solution
First, we create a pipeline to ingest the historical data and find the customer segments and their voucher values.
Next, for every requested customer we calculate its segment and find the voucher value from the database.
To provide more detail, the steps are as follows:
- first, we need a series of tasks to do the following jobs: 
  - download data from the provided link: data is in parquet file format and is manipulated using pandas 
  - convert it to CSV: by doing so we can store it in the database easily
  - store data in the database: based on the amount of data and pipeline processes, a SQL database is chosen for this step
  - clean the data: some rule-based cleaning is done in this step which is described later in detail.
  - calculate the segments: this is done by a SQL query to use the database optimizations and reduce the data
    conversion overhead from SQL to Python and vice versa.
    
  these tasks are scheduled and managed by airflow. After this step, we have the required data to respond to the API
  calls in the database. 

- second, we need to write an API endpoint to respond to API calls. This task is done using
FastAPI. It has some interesting features for scalability and automated API DOCs and easy quickstart. Each API call is 
  received by FastAPI and the query parameters are sent to DB using SQLAlchemy. finally, the result is sent back to the user.
  
## data cleaning
For the data cleaning part, some rule-based conditions are applied to Peru's country data. These rules are as follows:
- for some records, the `total_orders` field is empty and can not be used for segmentation. (8594 records)
- for some records, the `voucher_amount` field is empty and can not be used for segmentation. (13950 records)
- for some records, the `total_orders` field is zero, but the `first_order_ts` or `last_order_ts` fields have some dates in them. these records are ignored. (11116 records)
- for some records, the `total_orders` field is 1, but the `first_order_ts` and `last_order_ts` are at different times. these records are ignored. (4503 records) 

the total number of records of Peru's country is 106547 which the above conditions remove 33866 records and we build segments based on 72681 records. 

NOTE: the last timestamp of data is 2020-05-28 and their date difference from today is large. To be able to
  produce different segments, there is a `TODAY` environment variable in env files which can be tweaked to change the final day of calculations.  

## how to run

to run the project only docker and docker-compose are needed to be installed.

NOTE: make sure `8000` and `8080` and `5432` ports are not used by processes. These ports are used for API endpoint and airflow web UI and Postgres database.

The project is based on docker containers and a docker-compose file runs all the containers. Some sample env variables
are provided in the project to make it easy to run and test. But for real-world usages take care of the env variables
and use strong credentials.

`docker-compose up -d` will build the API image and create all the containers and run the project.

then use a web browser to access the airflow web UI to trigger the pipeline called `customer_segmentation`. It can be found in 
[http://127.0.0.1:8080/](http://127.0.0.1:8080/) using the credentials:

user: `airflow`

pass: `airflow`

When the pipeline is finished successfully, you can use the endpoint [http://127.0.0.1:8000/segmentation-voucher/](http://127.0.0.1:8000/segmentation-voucher/) to get a voucher per user.
Also, the API documentation can be found [here](http://127.0.0.1:8000/redoc/).

the sample curl command is also as follows:
```
curl --header "Content-Type: application/json" \
    --request POST \
     --data '{"customer_id": 123, "country_code": "Peru", "last_order_ts": "2018-05-03 00:00:00", "first_order_ts": "2017-05-03 00:00:00", "total_orders": 15, "segment_name": "recency_segment"}' \
     http://127.0.0.1:8000/segmentation-voucher/
```

or using python:
```
import requests

url = 'http://127.0.0.1:8000/segmentation-voucher/'
cusromer_object = {
    "customer_id": 123,
    "country_code": "Peru",
    "total_orders": 15,
    "last_order_ts": "2018-05-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "segment_name": "recency_segment",
}

response = requests.post(url, json=cusromer_object)

print(response.text)
```

## tests
This project uses the pytest framework for unit testing.
some API tests are provided using pytest to test if API calls are working fine. To run tests, we need to exec into the api container and run pytest.
```
docker exec -it app-api bash
$ pytest
```
NOTE: these unit tests use the same database which is used by the main app. So after running pytest, previous results will be deleted from the database and the pipeline must run again.
It can be improved by providing another database for testing.

## TODO:
- add more tests and use separate database for unit tests
- add CI
- add type hints and pre-commit checks
