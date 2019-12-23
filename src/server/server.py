import os, sys, shutil, base64, time
import storage.libElasticDB  as esdb
sys.path.append('..')
from src import config
import utils

class ServerHandler(object):
    def __init__(self, server):
        self.server = server

    def test(self, **kargs):
        return self.server.test()

    def queryText(self, method, **kargs):
        if 'GET' == method:
            return self.server.query_text(**kargs)

    def pdfsInfo(self, method, **kargs):
        if 'GET' == method:
            return self.server.pdfs_info(**kargs)

    def deletePaper(self, method, **kargs):
        if 'GET' == method:
            return self.server.delete_pdf(kargs['name'])

    def downloadPdf(self, method, **kargs):
        if 'GET' == method:
            return self.server.download_pdf(kargs['pdf_name'])

    def downloadResult(self, method, **kargs):
        if 'GET' == method:
            return self.server.download_result(kargs['result_file'])

    def indexFile(self, method, fileName, fileData):
        if 'POST' == method:
            return self.server.index_uploaded_pdf( fileName, fileData)

    def checkPdf(self, method, fileName, fileData):
        if 'POST' == method:
            pdfutils = utils.PDFUtils()
            pdf_path = pdfutils.save_pdf_file(fileName, fileData, config.WORK_DIR)
            return self.server.check_uploaded_pdf(pdf_path)

class Server(object):
    def __init__(self):
        pass

    def get_db(self):
        return esdb.ElasticDB()

    def test(self):
        db = self.get_db()
        return db.get_mapping(index=config.PAPERS_INDEX, doc_type=config.PAPERS_DOC_PAGES)

    def index_creater(self):
        es = self.get_db()
        mapping = {
            "mappings": {
                "pdf": {
                    "properties": {
                        "file": {
                            "type": "attachment",
                            "fields": {
                                "content": {
                                    "type": "string",
                                    "term_vector": "with_positions_offsets",
                                    "store": True
                                }
                            }
                        }
                    }
                }
            }
        }
        res = es.createIndex(index=config.PAPERS_INDEX, body=mapping)
        return res

    def index_remover(self):
        es = self.get_db()
        res = es.deleteIndex(index=config.PAPERS_INDEX)
        return res

    def insert_pdf(self, pages_dir, pdf_path):
        es = self.get_db()
        pdf_name = os.path.basename(pages_dir).rstrip('.pdf')
        nr_pages = 0
        for page in os.listdir(pages_dir):
            if not page.endswith('.pdf'):
                continue
            nr_pages += 1
            page_path = os.path.join(pages_dir, page)
            page_nr = page.rstrip('.pdf')
            f = open(page_path, 'rb')
            encoded_pdf = base64.b64encode(f.read())
            f.close()
            body = {'file': encoded_pdf}
            es.insert(index=config.PAPERS_INDEX, doc_type=config.PAPERS_DOC_PAGES, id="%s_%s" % (pdf_name, page_nr), body=body)
        body = {
            'pdf_name': pdf_name,
            'nr_pages': nr_pages,
            'pdf_size': os.path.getsize(pdf_path),
            'insert_time': int(time.time())
        }
        res = es.insert(index=config.PAPERS_INDEX, doc_type=config.PAPERS_DOC_META, id="%s" % pdf_name, body=body)
        return res

    def index_pdf(self, pdf_path):
        pdfutils = utils.PDFUtils()
        pdf_name = os.path.basename(pdf_path)
        pdf_storage_path = os.path.join(config.PDF_STORAGE, pdf_name)
        if not os.path.isfile(pdf_storage_path):
            shutil.copy(pdf_path, pdf_storage_path)
        self.sanitize_pdf_name(pdf_storage_path)
        pdf_path = pdf_storage_path
        pages_dir = pdfutils.divide_pdf(pdf_path)
        res = self.insert_pdf(pages_dir, pdf_path)
        if os.path.isdir(pages_dir):
            shutil.rmtree(pages_dir)
        print "Inserted: %s" % pdf_name
        return res

    def index_pdf_dir(self, dir_path):
        for fis in os.listdir(dir_path):
            if not fis.endswith('.pdf'):
                continue
            pdf_name = fis.rstrip('.pdf')
            possible = self.get_pdf_meta(pdf_name)
            if possible:
                print "%s - exists" % fis
                print possible
                continue
            pdf_path = os.path.join(dir_path, fis)
            res = self.index_pdf(pdf_path)
            print 'Status %s - %s' % (str(fis), str(res))

    def index_uploaded_pdf(self, file_name, file_data):
        pdfutils = utils.PDFUtils()
        pdf_path = pdfutils.save_pdf_file(file_name, file_data, config.TEMP_PDF_STORAGE)
        print self.index_pdf(pdf_path)
        os.remove(pdf_path)

    def count_pdfs(self):
        es = self.get_db()
        return es.count(index=config.PAPERS_INDEX, doc_type=config.PAPERS_DOC_META)

    def get_pdf_meta(self, pdf_name):
        es = self.get_db()
        return es.get(index=config.PAPERS_INDEX, doc_type=config.PAPERS_DOC_META, id=pdf_name)

    def delete_pdf(self, pdf_name):
        es = self.get_db()
        pdf_data = self.get_pdf_meta(pdf_name)
        if not pdf_data:
            print pdf_name + " does not exist"
            return
        for page in range(1, pdf_data['nr_pages']+1):
            es.delete(index=config.PAPERS_INDEX, doc_type=config.PAPERS_DOC_PAGES, id=pdf_name + '_' + str(page))
        es.delete(index=config.PAPERS_INDEX, doc_type=config.PAPERS_DOC_META, id=pdf_name)
        if os.path.isfile(os.path.join(config.PDF_STORAGE, pdf_name + '.pdf')):
            os.remove(os.path.join(config.PDF_STORAGE, pdf_name + '.pdf'))

    def download_pdf(self, pdf_name):
        if os.path.isfile(os.path.join(config.PDF_STORAGE, pdf_name + '.pdf')):
            fd = open(os.path.join(config.PDF_STORAGE, pdf_name + '.pdf'))
            return pdf_name, fd
        return None, None

    def download_result(self, result_file):
        if os.path.isfile(os.path.join(config.WORK_DIR, result_file)):
            fd = open(os.path.join(config.WORK_DIR, result_file))
            return result_file, fd
        return None, None

    def sanitize_pdf_name(self, pdf_path):
        pdf_name = os.path.basename(pdf_path)
        pdf_name = pdf_name.replace('%','_')
        os.rename(pdf_path, os.path.join(os.path.dirname(pdf_path), pdf_name))

    def query_phrase(self, phrase):
        es = self.get_db()
        query = {
            "query": {
                "match_phrase": {
                    "file.content": phrase
                }
            },
            "fields": ["_id"],
            "highlight": {
                "fields": {
                    "file.content": {
                    }
                }
            }
        }
        res = es.query(index=config.PAPERS_INDEX, query=query)
        return res

    def sentence_split(self, txt, extra=None):
        if extra:
            txt = txt.replace(": ",". ").replace('" ',". ").replace("; ",". ").replace("\n\n",". ")
        phrases = txt.split('. ')
        good_phrases = []
        for phrase in phrases:
            stripped_phrase = phrase.strip()
            if len(stripped_phrase) < config.MINIMUM_PHRASE_LENGTH:
                continue
            elif len(stripped_phrase) > config.MAXIMUM_PHRASE_LENGTH:
                words = stripped_phrase.split()
                group = ""
                for w in words:
                    group = group + " " + w
                    if len(group) > config.MAXIMUM_PHRASE_LENGTH:
                        good_phrases.append(group.lstrip())
                        group = ""
                if group:
                    good_phrases.append(group.lstrip())
            else:
                good_phrases.append(stripped_phrase)
        return good_phrases

    def paragraph_split(self, txt):
        paragraphs =  txt.split("\n\n")
        good_paragraphs = []
        for paragraph in paragraphs:
            stripped_paragraph = paragraph.strip()
            if len(stripped_paragraph) < config.MINIMUM_PARAGRAPH_LENGTH:
                continue
            elif len(stripped_paragraph) > config.MAXIMUM_PARAGRAPH_LENGTH:
                phrases = self.sentence_split(paragraph)
                group = ""
                for p in phrases:
                    group = group + ". " + p
                    if len(group) > config.MAXIMUM_PARAGRAPH_LENGTH:
                        good_paragraphs.append(group.lstrip(". "))
                        group = ""
                if group:
                    good_paragraphs.append(group.lstrip(". "))
            else:
                good_paragraphs.append(paragraph)
        return good_paragraphs

    def query_text(self, **kargs):
        txt = kargs['query']
        phrases = self.sentence_split(txt, extra=True)
        result = {
            'phrase_hits':[],
            'score': 0,
            'sources': 0,
            'phrases': 0
        }
        sources = []
        good_phrases = len(phrases)
        for phrase in phrases:
            res = self.query_phrase(phrase)
            hits_nr = len(res['hits'])
            if not hits_nr:
                continue
            winner = res['hits'][0]
            result['phrase_hits'].append({
                'paper': winner['_id'].rsplit('_', 1)[0],
                'page': winner['_id'].rsplit('_', 1)[1],
                'content': winner['highlight']['file.content'][0],
                'stripped_phrase': phrase
            })
            if winner['_id'].rsplit('_', 1)[0] not in sources:
                sources.append(winner['_id'].rsplit('_', 1)[0])
        if good_phrases:
            result['score'] = len(result['phrase_hits']) * 100 /  good_phrases
        result['sources'] = len(sources)
        result['phrases'] = good_phrases
        return result

    def pdfs_info(self, **kargs):

        es = self.get_db()
        q = {
            "query": {
                "filtered": {
                    "filter": {
                        "type": {"value": config.PAPERS_DOC_META}
                    }
                }
            },
            "sort": [
                {"insert_time": {"order": "desc"}}
            ],
            'size': 10000
        }
        res = es.query(index=config.PAPERS_INDEX, query=q)
        ret_data = []
        for hit in res['hits']:
            ret_data.append({'pdf':hit['_source']['pdf_name'],
                             'pages': hit['_source']['nr_pages'],
                             'size': hit['_source']['pdf_size'],
                             'insert_time':  hit['_source']['insert_time']})
        return ret_data

    def check_uploaded_pdf(self, pdf_path):
        pdfutils = utils.PDFUtils()
        pdf_name = os.path.basename(pdf_path)
        #pdf_path = pdfutils.save_pdf_file(file_name, file_data, config.WORK_DIR)
        result = {
            'pdf_name': pdf_name,
            'top_results': {},
            'score': 0,
            'paragraphs': 0,
            'hits': 0,
            'sources': 0,
            'error':0
        }
        paragraph_hits = []
        pdf_text = pdfutils.pdf_to_txt_tika(pdf_path)
        if not pdf_text:
            pdf_text = pdfutils.pdf_to_txt(pdf_path)
            result['error'] = 1
        if not pdf_text:
            result['error'] = 2
            return result
        paragraphs = self.paragraph_split(pdf_text)
        if len(paragraphs) < config.MINIMUM_PARAGRAPH_NUMBER:
            paragraphs = self.sentence_split(pdf_text)
        result['paragraphs'] = len(paragraphs)
        for paragraph in paragraphs:
            res = self.query_phrase(paragraph)
            hits_nr = len(res['hits'])
            if not hits_nr:
                continue
            winner = res['hits'][0]
            paragraph_hits.append({
                'paper': winner['_id'].rsplit('_', 1)[0],
                'page': winner['_id'].rsplit('_', 1)[1],
                'content': winner['highlight']['file.content'][0],
            })
            result['hits'] += 1
            if winner['_id'].rsplit('_', 1)[0] not in result['top_results']:
                result['top_results'][winner['_id'].rsplit('_', 1)[0]] = {
                    'pages': 0,
                    'hits': 0
                }
            result['top_results'][winner['_id'].rsplit('_', 1)[0]]['pages'] += 1
            result['top_results'][winner['_id'].rsplit('_', 1)[0]]['hits'] += 1

        if result['paragraphs']:
            result['score'] = result['hits'] * 100 / result['paragraphs']
        result['sources'] = len(result['top_results'])
        result['top_results'] = sorted(result['top_results'].items(), key=lambda x: x[1]['hits'], reverse=True)
        result['top_results'] = result['top_results'][:10]

        result_file = pdf_name.rstrip('.pdf') + "_result" + ".txt"
        f = open(os.path.join(config.WORK_DIR, result_file), 'wb')
        pprint.pprint(result,stream=f)
        pprint.pprint(paragraph_hits,stream=f)
        f.close()

        result['result_file'] = result_file

        return result

if __name__ == '__main__':
    server = Server()
    #server.index_pdf_dir('/home/ovidiu/Workspace/Facultate/licenta/server-project/pdf_storage')
    #print server.get_pdf_meta('Einstein_Relativity')
    #print server.index_remover()
    #print server.index_creater()
    #print server.count_pdfs()
    #print server.query_phrase("industry standards, contractual obligations, and even self-imposed obligations")
    x = server.check_uploaded_pdf('/home/ovidiu/Workspace/Facultate/licenta/server-project/work_dir/digital disaster.pdf')
    import pprint
    pprint.pprint(x)

