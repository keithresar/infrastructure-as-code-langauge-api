#!/usr/bin/env python

#
# Application that executes that languagelayer API against a polled web site to
# determine the langauge.  Application accepts the following environment variables
#
#   o LANGUAGELAYER_API_KEY
#   o ELASTICACHE...
#

HTTP_PORT = 8080
WAIT_TIME_SECS = 2

import re
import os
import sys
import time
import json
import requests
from urlparse import parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer



class Handler(BaseHTTPRequestHandler):

    def send_error(self,error,message):
        self.send_response(error)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'error': message}))


    def get_target(self,url):
        r = requests.get(url)
        if r.status_code<200 or r.status_code>=300:
            raise()

        return(r.text)


    def get_target_body(self,target_body):
        try:
            body = re.sub("<.*?>","",re.sub("<.*body.*>(.+?)</.*body.*>","\1",target_body,flags=re.IGNORECASE))
            if not len(body):  raise()
        except:
            raise()

        return(body)


    def languagelayer_detection(self,text):
        # Does not accept post requests, so truncate query
        if len(text)>800:  text = text[0:800]

        r = requests.get("http://apilayer.net/api/detect",
                          params = {'access_key': LANGUAGELAYER_API_KEY, 'query': text})
        if r.status_code<200 or r.status_code>=300:
            raise()

        return(r.text)


    def do_GET(self):
        # Verify request has URL
        try:
            req_qs =  parse_qs(self.path[2:])
            url = req_qs['url'][0]
        except:
            self.send_error(400,"Required 'url' parameter missing")
            return

        # TODO Verify cache entry (if enabled)

        # Get target URL
        try:
            target_response_text = self.get_target(url)
        except:
            self.send_error(500,"Error fetching requested url")
            return

        # Extract target body
        try:
            target_response_body = self.get_target_body(target_response_text)
        except:
            self.send_error(500,"Error extracting requested url text")
            return

        # Issue Languagelayer request
        try:
            language_layer_response = self.languagelayer_detection(target_response_body)
        except:
            self.send_error(500,"Error communicating with languagelayer API")
            return


        # TODO Store in cache (if enabled)

        # TODO Pause to add slowdown if cache not used
        #time.sleep(WAIT_TIME_SECS)

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        # Send the response message
        self.wfile.write(language_layer_response)
        return


try:
    LANGUAGELAYER_API_KEY = os.environ['LANGUAGELAYER_API_KEY']
except:
    sys.stderr.write("Missing LANGUAGELAYER_API_KEY\n")
    sys.exit(1)


try:
    server = HTTPServer(('', HTTP_PORT), Handler)
    print 'Started httpserver on port ' , HTTP_PORT
    server.serve_forever()

except:
    print 'Shutting down the web server'
    server.socket.close()

