from config import DB_Config
from pymongo import errors

db_name = DB_Config.db_name


class Usertranscation():
    def __init__(self):
        self.db = db_name

    def get_data(self, collection_name):
        collection = self.db[collection_name]
        users = collection.find()
        return list(users)

    def save(self, collection_name, data):
        collection = self.db[collection_name]
        return collection.insert_one(data)

class Beneficiarydetails:
    collection = DB_Config.col_beneficiarydetails
     
    @classmethod
    def save(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_data(cls, data):
        return list(cls.collection.find(data))
    
    @classmethod
    def get_user_accno(cls, userid):
        return list(cls.collection.find({'userid': userid}, {"Name","Accno"}))
    
    @classmethod
    def get_data_one(cls, data):
        return list(cls.collection.find_one(data))
    
    @classmethod
    def get_data_accno(cls, userid, idvalue, accno, accvalue):
        query = {userid: idvalue, accno: accvalue}
        #return dict(cls.collection.find_one({"userid":userid,"Accno":accno}))
        return cls.collection.find_one(query)
    
    @classmethod
    def get_count(cls, data, limit=None):
        count = cls.collection.count_documents(data, limit=limit)
        return count
    
    @classmethod
    def delete_data(cls, user_id, accno):
        result = cls.collection.delete_one({'userid': user_id, 'Accno': accno})
        return result.deleted_count > 0


class Userdata:
    collection = DB_Config.col_userdata

    @classmethod
    def save(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_data(cls, data):
        return dict(cls.collection.find(data))
    
    
    @classmethod
    def get_userdata(cls, userid, idvalue):
        query = {userid: idvalue}
        #return dict(cls.collection.find_one({"userid":userid,"Accno":accno}))
        return cls.collection.find_one(query)
    
    @classmethod
    def get_data_one(cls, data):
        return dict(cls.collection.find_one(data))
    
    @classmethod
    def update(cls, data, updatedata):
        return cls.collection.update_one(data, updatedata)
    
    @classmethod
    def find_and_sort_documents(cls, sort_field='_id', sort_order= -1, limit1=1):
        cursor = cls.collection.find().sort(sort_field, sort_order).limit(limit1)
        return list(cursor)
    
    @classmethod
    def find_data_one(cls, data):
       try:
        output = cls.collection.find_one(data)
        if output:
            return dict(output)
        else:
            return 0
       except Exception as e:
           return {'error': str(e)}
