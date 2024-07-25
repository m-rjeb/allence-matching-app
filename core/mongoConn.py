from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.server_api import ServerApi


class Connection:
    __client: MongoClient

    def __init__(self, connection_uri) -> None:
        self.connection_url = connection_uri
        self.__client = MongoClient(host=self.connection_url, server_api=ServerApi("1"))

    def use_db(self, db_name):
        return self.__client[db_name]

    def close_connection(self) -> None:
        self.__client.close()


class Collections:
    __db: ...
    __collection: ...

    def __init__(self, db: str) -> None:
        self.__db = db

    def use_collection(self, collection_name: str) -> None:
        self.__collection = self.__db[collection_name]

    def create(self, data: dict) -> str:
        inserted = self.__collection.insert_one(data)
        return inserted.inserted_id

    def findById(self, document_id):
        return self.__collection.find_one({"_id": ObjectId(document_id)})

    def findByUsername(self, username):
        return self.__collection.find_one({"username": username})

    def findAll(self):
        return self.__collection.find()

    def update(self, document_id: str, data: dict):
        updated = self.__collection.update_one(
            {"_id": ObjectId(document_id)}, {"$set": data}
        )
        return updated.modified_count

    # deleteMany("status", ["inactive", "blocked"]) ==> delete documents that have inactive and blocked status
    def deleteMany(self, key: str, values: list[any]) -> int:
        deleted = dict()
        for value in values:
            deleted[value] = self.__collection.deleteAll(key, value)
        return deleted

    # deleteAll(key="status", value="inactive") ==> delete only documents that have inactive status
    def deleteAll(self, key, value):
        deleted = (
            self.__collection.delete_many({key: value})
            if key != "_id"
            else self.__collection.delete_many({"_id": ObjectId(value)})
        )
        return deleted.deleted_count

    def deleteOne(self, document_id) -> int:
        deleted = self.__collection.delete_one({"_id": ObjectId(document_id)})
        return deleted.deleted_count
