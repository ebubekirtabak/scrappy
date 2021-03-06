from pymongo import MongoClient
import logger


def connect_database(database):
    print(database)
    client = MongoClient(database['uri'])
    try:
        if database['name'] in client.list_database_names():
            db = client[database['name']]
            return db
        else:
            print('Database not exixts, create database: ' + database['name'])
            db = client[database['name']]
            return db
    except Exception as e:
        print("connect_database() " + str(type(e)) + " Error:", str(e))
        return 400


def get_server_status(db):
    try:
        return db.command("serverStatus")
    except Exception as e:
        print(e)
        return 0


def insert(db, collection, data):
    if db != 400:
        try:
            mycol = db[collection]
            result = mycol.insert_one(data)
            if result.inserted_id is not None:
                logger.Logger().set_log("insert data")
            else:
                logger.Logger().set_error_log("mongo insert data error")
        except Exception as e:
            logger.Logger().set_error_log("mongoDB inser Error: " + str(e))
            # type, value, traceback = sys.exc_info()
            # print('Error opening %s: %s' % (value.filename, value.strerror))
            print(e)
            return 400


def get_find_one(db, collection, query):
    return db[collection].find(query)


def find_and_delete(db, collection, query):
    return db[collection].find_one_and_delete(query)


def find_all(db, collection, query):
    return db[collection].find_all(query)


def get_length(db, collection):
    return db[collection].count()


def isExists(db, collection, data):
    mycol = db[collection]
    return mycol.find(data).count() > 0
