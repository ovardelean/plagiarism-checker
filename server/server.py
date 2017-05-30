import os, sys, json
import storage.libElasticDB  as esdb

class Server(object):
    def __init__(self):
        pass

    def get_db(self):
        return esdb.ElasticDB()

    def test(self):
        db = self.get_db()
        return db.get_mapping(index='papers',doc_type='pdf')