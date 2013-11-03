#!/usr/bin/env python

import logging
from functools import partial
from contextlib import contextmanager

import tornado.ioloop
import tornado.web
from tornado.escape import json_encode,json_decode


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        """display the main template"""
        self.render('main.html')


class AjaxHandler(tornado.web.RequestHandler):
    def get(self):
        raise tornado.web.HTTPError('must use post')
    
    @tornado.web.asynchronous
    def post(self):
        # json decode body
        body = json_decode(self.request.body)
        func = body['function']
        logging.info('json function: %r',body['function'])

        ret = {'ret':False}
        if body['function'] == 'getGCD':
            pass
        else:
            raise Exception('function invalid')
        
        self.write(json_encode(ret))
        self.finish()
        
    def write_error(self,status_code,**kwargs):
        logging.error('error %r',status_code)
        self.write(json_encode({'ret':None,'error':[status_code]}))
        self.finish()



if __name__ == '__main__':
    import time
    from threading import Thread
    from optparse import OptionParser
    import webbrowser
    from socket import gethostname
    
    logging.basicConfig(level=logging.INFO)
    
    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', type='int', default=49382,
                      help='assign to port (default 49382)')
    parser.add_option('-b', '--browser', dest='browser', type='string',
                      default=None, help='browser type to open')
    parser.add_option('--no-browser', dest='open_browser',
                      action='store_false', default=True,
                      help='do not open browser')
    
    (options, args) = parser.parse_args()
    
    # prepare to open the browser
    url = 'http://'+gethostname()+':'+str(options.port)+'/#'
    #url += ','.join(files)
    if options.open_browser:
        try:
            browser = webbrowser.get(options.browser)
        except webbrowser.Error as e:
            logging.warn('No web browser found: %s',e)
            options.open_browser = False
    
    # prepare tornado
    application = tornado.web.Application([
        (r'/ajax', AjaxHandler),
        (r'/', MainHandler),
    ], static_path='static', template_path='templates')
    application.listen(options.port)
    
    # actually open the browser
    if options.open_browser:
        browser.open(url)
    else:
        print 'open browser and go to'
        print url
    
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.error('STOPPED')
