import sys
import os
import argparse
import shutil

sys.path.insert(0, os.path.abspath(".."))
from server.server import Server
from server.http_server.cherrypy_server import CherrypyHTTPServer

def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", type=str)
    # HTTP server
    parser.add_argument("-P", "--port", type=int, default=8080)
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0")
    parser.add_argument("-C", "--connections", type=int, default=10)
    parser.add_argument("-d", "--debug", type=bool, default=False)
    return parser

def parse_args(args):
    return get_arg_parser().parse_args(args)

def main(args):

    http_server = CherrypyHTTPServer({
        "server.socket_port" : args.port, 
        "server.socket_host" : args.host,
        "server.thread_pool" : args.connections,
        "server.max_request_body_size" : 1024 * 1024 * 1024, 
        "log.screen" : True, 
        "environment" : "test_suite" if args.debug else "production",
        "tools.sessions.on": True, 
        "tools.sessions.timeout" : 24 * 60,     # 24 hours
        "engine.autoreload.on": True,
        'tools.proxy.on': True,
        'log.access_file':"access.log"
    })

    handler = Server()

    http_server.set_handler(handler)
    http_server.start()

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    exit(main(args))
