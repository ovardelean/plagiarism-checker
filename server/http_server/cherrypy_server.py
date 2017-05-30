import cherrypy
import cherrypy.lib.static
import os, json

from cherrypy import HTTPRedirect

WEB_DIR = os.path.join(os.path.dirname(__file__), 'static')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

class HTTPServer(object):
    def set_handler(self, handler):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

class CherrypyHTTPServer(HTTPServer):
    def __init__(self, cp_config, service_config=None):
        self.cp_config = cp_config
        self.service_config = service_config or {
            "/" : {
                "tools.staticdir.root" : STATIC_DIR,
                "tools.staticdir.debug" : True,
            },
            "/static/js" : {
                "tools.staticdir.on" : True,
                "tools.staticdir.dir" : "js"
            },
            "/static/css" : {
                "tools.staticdir.on" : True,
                "tools.staticdir.dir" : "css",
            },
            "/static/img" : {
                "tools.staticdir.on" : True,
                "tools.staticdir.dir" : "img",
            },
            #"/static/html" : {
            #    "tools.staticdir.on" : True,
            #    "tools.staticdir.dir" : "html",
            #},
        }
        self.handler = None

    def set_handler(self, handler):
        self.handler = handler

    def start(self):
        if self.handler is None:
            raise ValueError, "Handler not set, use set_handler first!"
        g_handler = self.handler

        cherrypy.config.update(self.cp_config)

        class IndexHandler(object):
            """
            /
            """
            @cherrypy.expose
            def index(self, **kargs):
                html_file = open(os.path.join(WEB_DIR, "html", "index.html")).read()
                return html_file

            @cherrypy.expose
            def test(self, **kargs):
                return json.dumps(g_handler.test(**kargs))

            @cherrypy.expose
            def indexFile(self, **kargs):
                return json.dumps(g_handler.indexFile(**kargs))

            @cherrypy.expose
            def indexFilePath(self, **kargs):
                return json.dumps(g_handler.indexFilePath(**kargs))


        root = IndexHandler()

        import pprint
        pprint.pprint(cherrypy.config)
        cherrypy.tree.mount(root, "/", self.service_config)
        cherrypy.engine.start()
        cherrypy.engine.block()
