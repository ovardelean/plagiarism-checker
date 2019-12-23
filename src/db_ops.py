import sys

from src.server import Server

def main(args):

    server = Server()
    if args[1] == 'createIndex':
        server.index_creater()
    elif args[1] == 'deleteIndex':
        server.index_remover()
    elif args[1] == 'insertPdfDir':
        server.index_pdf_dir(args[2])
    elif args[1] == 'deletePdf':
        server.delete_pdf(args[2])

if __name__ == "__main__":
    main(sys.argv)
