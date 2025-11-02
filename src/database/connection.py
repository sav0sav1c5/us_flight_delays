from pymongo import MongoClient

def connect_to_database(uri: str, db_name: str):
    """
    Connect to MongoBD and return database object.
    """

    client = MongoClient(uri)

    client.admin.command('ping')

    database = client[db_name]

    return client, database