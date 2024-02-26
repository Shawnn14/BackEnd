from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
from fastapi import HTTPException, status
from pyspark.sql import SparkSession

def handle_mongodb_spark_connection(uri: str, master_url: str, driver_host_name: str):
    try:
        spark = SparkSession \
            .builder \
            .master(master_url) \
            .config("spark.mongodb.input.uri", uri) \
            .config("spark.driver.host", driver_host_name) \
            .config('spark.jars.packages','org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
            .getOrCreate()
        
    except ConnectionFailure as f:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= f
        )
    return spark

def handle_mongodb_connection(uri: str):
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
    except ConnectionFailure as f:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= f
        )
    return client