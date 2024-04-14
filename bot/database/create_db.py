from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId
from helper_classes.assistant import MinorOperations

helper = MinorOperations()

async def create_db():
    try:
        new_db = AsyncIOMotorClient(f'mongodb://{helper.get_login()}:{helper.get_password()}@mongodb:27017')
        new_table = new_db["zoom_tg_bot"]
        col = new_table['current_data_f_new_meeting']
        obj = {"_id": ObjectId("65f7110e4e9a3762bba43801"), "users": []}
        await col.insert_one(obj)
    except Exception as e:
        print(e)