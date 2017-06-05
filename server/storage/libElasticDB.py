import time
import elasticsearch
from elasticsearch import helpers

class ElasticDB(object):
    def __init__(self, host='localhost', port='9200', request_timeout=15*60):
        self.host = host
        self.port = port
        self.request_timeout = request_timeout
        self.lastCrash = 0
        self.es = None
        self.connect()
        
    default_index = 'test'
    default_doc_type = 'test'
    
    def connect(self, excOnFail=1, timeout = 360):
        self.es = None
        try:
            self.es = elasticsearch.Elasticsearch([{'host':self.host, 'port': self.port}], timeout = timeout)
            self.lastCrash = 0
        except:
            print 'Failed connecting to ElasticSearch [%s]:[%s]' % (self.host, self.port)
            self.es = None
            if excOnFail:
                raise

    def __repr__(self):
        return '<libElasticDB.ElasticDB(host=\'%s\', port=%s) at %s>' % (self.host, self.port, hex(id(self)))

    def close(self):
        self.es = None
    
    def execute(self, what, excOnFail=1, *args, **kargs):
        logExc = 1
        timeout = None
        if 'logExc' in kargs:
            logExc = kargs['logExc']
            del kargs['logExc']
        
        if 'timeout' in kargs:
            timeout = kargs['timeout']
            del kargs['timeout']
        
        if self.lastCrash:
            print 'LastCrash was set; recreating the connection...'
            self.connect(excOnFail=excOnFail)
        
        if not self.es:
            self.connect(excOnFail=excOnFail)
            if not self.es:
                raise Exception, 'No ElasticDB connection; can\'t execute query [%s]!' % what
        
        try:
            if hasattr(what, '__call__'):
                fun = what
            else:
                fun = getattr(self.es, what)
            res = fun(*args, **kargs)
            self.lastCrash = 0
            return res
        except:
            self.lastCrash = time.time()
            if logExc:
                print 'ElasticDB: %s() failed for args: [%s][%s]' % (what, str(args), str(kargs))
            if excOnFail:
                raise
        return None

    def createIndex(self, index, ignore=None, body = None, excOnFail=1, logExc=1):
        return  self.execute(self.es.indices.create, excOnFail, index=index,body = body, ignore=ignore or [], logExc=logExc)
        
    def deleteIndex(self, index, excOnFail=1, logExc=1):
        return  self.execute(self.es.indices.delete, excOnFail, index=index, logExc=logExc)

    def existsIndex(self, index, excOnFail=1, logExc=1):
        return  self.execute(self.es.indices.exists, excOnFail, index=index, logExc=logExc)

    def insert(self, index=default_index, doc_type=default_doc_type, id=1, body=None, ignore=None, refresh = True, excOnFail=1, logExc=1, timeout=60):
        insRes = self.execute('index', excOnFail, index=index, doc_type=doc_type, id=id, body=body, ignore=ignore or [],refresh=refresh, logExc=logExc, timeout=timeout)
        if not insRes or 'error' in insRes:
            return False
        return True

    def bulk(self,body, excOnFail=1, logExc=1):
        return  self.execute(helpers.bulk, excOnFail, self.es, body, logExc=logExc)

    def update(self, index=default_index, doc_type=default_doc_type, id=1, body=None, ignore=None, refresh=True, excOnFail=1, logExc=1):
        updRes = self.execute('update', excOnFail, index=index, doc_type=doc_type, id=id, body={'doc': body}, ignore=ignore or [], refresh=refresh, logExc=logExc)
        if not updRes or 'error' in updRes:
            return False
        return True

    def get(self, index=default_index, doc_type=default_doc_type, id=1, ignore=404, excOnFail=1, logExc=1):
        getRes = self.execute('get', excOnFail, index=index, doc_type=doc_type, id=id, ignore=ignore or [], logExc=logExc)
        if not getRes or not getRes['found']:
            return None
        return getRes['_source']
        
    def getMore(self, index=default_index, doc_type=default_doc_type, id=1, ignore=404, excOnFail=1, logExc=1):
        getRes = self.execute('get', excOnFail, index=index, doc_type=doc_type, id=id, ignore=ignore or [], logExc=logExc)
        if not getRes or not getRes['found']:
            return None
        return getRes

    def get_version(self, index=default_index, doc_type=default_doc_type, id=1, ignore=None, excOnFail=1, logExc=1):
        versionRes = self.execute('get', excOnFail, index=index, doc_type=doc_type, id=id, ignore=ignore or [], logExc=logExc)
        if not versionRes or not versionRes['found']:
            return None
        return versionRes['_version']
    
    def delete(self, index=default_index, doc_type=default_doc_type, id=1, ignore=None, refresh=True, excOnFail=1, logExc=1):
        self.execute('delete', excOnFail, index=index, doc_type=doc_type, id=id, ignore=ignore or [], refresh=refresh, logExc=logExc)

    def get_id_list(self, index=default_index, doc_type = None, size = 10000,sort_list = None, excOnFail=1, logExc=1):
        sort_list = sort_list or []
        searchRes = self.execute('search', excOnFail, index=index, doc_type = doc_type, body={'query': {'match_all': {}}, 'size': size, 'fields': ['_id'], 'sort':sort_list},
                                 logExc=logExc)
        if not searchRes:
            return []
        return [d['_id'] for d in searchRes['hits']['hits']]
     
    def query(self, index=default_index, query = None, excOnFail=1, logExc=1):
        searchRes = self.execute('search', excOnFail, index=index, body=query, logExc=logExc)
        print 'Total hits: ', searchRes['hits']['total']
        return searchRes['hits']

    def count(self, index=default_index, doc_type=default_doc_type, body=None, ignore=None, excOnFail=1, logExc=1):
        countRes = self.execute('count', excOnFail, index=index, doc_type=doc_type, body=body, ignore=ignore or [], logExc=logExc)
        if not countRes or 'error' in countRes:
            return None
        return countRes['count']

    def get_mapping(self, index=default_index, doc_type=default_doc_type):
        ic = elasticsearch.client.IndicesClient(self.es)
        mapping = ic.get_mapping(index=index, doc_type=doc_type)
        return mapping
