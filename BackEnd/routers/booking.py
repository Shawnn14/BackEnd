from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response
from ..utils.read_config import read_config
from ..utils.exception import handle_mongodb_spark_connection, handle_mongodb_connection
from ..models.model import Booking, Ticket
from bson.objectid import ObjectId
import json
from pyspark.sql.functions import col

not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, 
    detail= 'Document or index no exits'
)

mongodb = read_config('mongodb-cloud')
uri = mongodb['uri']
master_url = mongodb['master_url']
driver_host_name = mongodb['driver_host_name']
db = mongodb['db']
flight_collection_name = mongodb['flight']
booking_collection_name = mongodb['booking']

router = APIRouter(
    prefix="/booking",
    tags=["booking"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get_list_flight", description='Get all flight')
async def get_flight_list():

    spark = handle_mongodb_spark_connection(uri, master_url, driver_host_name)

    try:
        dataFrame = spark.read \
                .format("com.mongodb.spark.sql.DefaultSource") \
                .option("database", db) \
                .option("collection", flight_collection_name) \
                .load()
        
        result = []
        for row in dataFrame.collect():
            result.append(row.asDict())

        return {'flight': result}
    except Exception as e:
        raise not_found_exception
    finally:
        spark.stop()
    


@router.get("/get_book", description='Get information about customer')
async def get_book(id: str = '65ae2c49da8523f7119ba48f'):

    spark = handle_mongodb_spark_connection(uri, master_url, driver_host_name)

    try:
        dataFrame = spark.read \
                .format("com.mongodb.spark.sql.DefaultSource") \
                .option("database", db) \
                .option("collection", booking_collection_name) \
                .load()
        
        filtered_df = dataFrame.filter(col("_id.oid") == id)
        result = []
        for row in filtered_df.collect():
            row_dict = row.asDict()
            _id_value = row_dict.pop('_id', None)
            result.append(row_dict)

        return {'flight': result[0]}
    except Exception as e:
        raise not_found_exception
    finally:
        spark.stop()

@router.get("/get_flight", description='Get flight by id')
async def get_flight(id: str = 'VNA0002'):

    spark = handle_mongodb_spark_connection(uri, master_url, driver_host_name)

    try:
        dataFrame = spark.read \
                .format("com.mongodb.spark.sql.DefaultSource") \
                .option("database", db) \
                .option("collection", flight_collection_name) \
                .load()
        
        filtered_df = dataFrame.filter(col("_id") == id)
        result = []
        for row in filtered_df.collect():
            result.append(row.asDict())

        return {'flight': result[0]}
    except Exception as e:
        raise not_found_exception
    finally:
        spark.stop()


@router.post("/booking_flight", description='Booking flight')
async def booking_flight(booking_info: Booking):
    booking_info_dict = booking_info.model_dump()

    client = handle_mongodb_connection(uri)
    database = client[db]
    booking_collection = database[booking_collection_name]
    flight_collection = database[flight_collection_name]

    try:
        data = {'flight_code': booking_info_dict['flight_code'],'name': booking_info_dict['name'],
                'phone': booking_info_dict['phone'],'email': booking_info_dict['email']
                }
        document = booking_collection.insert_one(data)
        
        flight_collection.update_one(
            { '_id': booking_info_dict['flight_code'] },
            { '$inc': { 'empty_seat': -1 } }
        )

        result = {'id_booking': str(document.inserted_id)}
    finally:
        client.close()

    return result

@router.put("/update_info", description='Update infomation')
async def update_info(ticket_info: Ticket):
    booking_info_dict = ticket_info.model_dump()

    client = handle_mongodb_connection(uri)
    database = client[db]
    booking_collection = database[booking_collection_name]
    booking_id = booking_info_dict['booking_id']

    try:
        new_data = {
            "$set": {'name': booking_info_dict['name'],
            'phone': booking_info_dict['phone'],'email': booking_info_dict['email']}
        }

        document = booking_collection.update_one(
            { '_id': ObjectId(booking_id) },
            new_data
        )
    finally:
        client.close()

    return {'result': 'Update successfull'}

@router.delete("/delete_info", description='Delete booking information')
async def update_info(id: str = '65ae2c49da8523f7119ba48f'):

    client = handle_mongodb_connection(uri)
    database = client[db]
    booking_collection = database[booking_collection_name]
    flight_collection = database[flight_collection_name]

    try:
        filter_condition = {'_id': ObjectId(id)}
        document = booking_collection.find_one(filter_condition)

        flight_code = document['flight_code']

        flight_collection.update_one(
            { '_id': flight_code },
            { '$inc': { 'empty_seat': 1 } }
        )

        booking_collection.delete_one(filter_condition)

    finally:
        client.close()

    return {'result': 'Delete successfull'}