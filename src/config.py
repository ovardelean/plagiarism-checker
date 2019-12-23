import os

WORK_DIR = os.path.join(os.path.dirname(__file__), 'work_dir')
PDF_STORAGE = os.path.join(os.path.dirname(__file__), 'pdf_storage')
TEMP_PDF_STORAGE = os.path.join(os.path.dirname(__file__), 'temp_pdf_storage')

PAPERS_INDEX = 'papers'
PAPERS_DOC_META = 'pdf_meta'
PAPERS_DOC_PAGES = 'pdf'

MINIMUM_PHRASE_LENGTH = 10
MAXIMUM_PHRASE_LENGTH = 1000
MINIMUM_PARAGRAPH_LENGTH = 100
MAXIMUM_PARAGRAPH_LENGTH = 5000
MINIMUM_PARAGRAPH_NUMBER = 10

TIKA_JAR = '/home/ovidiu/Workspace/Facultate/licenta/tika-1.14/tika-app/target/tika-app-1.14.jar'