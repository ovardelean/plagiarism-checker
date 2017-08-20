import os, sys, json, shutil, subprocess, base64, time
sys.path.append('..')
import config

class PDFUtils(object):

    def __init__(self):
        pass

    def divide_pdf(self, input_pdf):
        pdf_name = os.path.basename(input_pdf)
        pages_dir = os.path.join(config.WORK_DIR, pdf_name)
        if os.path.isdir(pages_dir):
            shutil.rmtree(pages_dir)
        os.mkdir(pages_dir)
        process = subprocess.Popen(['pdftk',
                                    input_pdf,
                                    'burst',
                                    'output',
                                    os.path.join(pages_dir, '%d.pdf')],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            print stderr
            return None
        return pages_dir

    def pdf_to_txt(self, input_pdf):
        pdf_name = os.path.basename(input_pdf)
        pdf_dir = os.path.dirname(input_pdf)
        output_pdf = os.path.join(pdf_dir, pdf_name.rstrip(".pdf") + "_%s" % str(int(time.time())) + ".txt")
        process = subprocess.Popen(['pdftotext',
                                    input_pdf,
                                    output_pdf],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            #print stderr
            return None
        data = open(output_pdf, 'rb').read()
        os.remove(output_pdf)
        return data

    def pdf_to_txt_tika(self, input_pdf):
        process = subprocess.Popen(['java',
                                    '-jar',
                                    config.TIKA_JAR,
                                    '-t',
                                    input_pdf],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            #print stderr
            return stdout
        return stdout

    def save_pdf_file(self, file_name, file_data, location):
        storage_path = os.path.join(location, file_name)
        f = open(storage_path, 'wb')
        f.write(file_data)
        f.close()
        return storage_path