#! /usr/bin/env python
#  Copyright (C) 2012 Sebastian Garcia, Maximo Martinez, Pablo Meyer
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# Author:
#       Sebastian Garcia, eldraco@gmail.com
#       Maximo Martinez, maximomrtnz@gmail.com
#       Pablo Meyer, pablitomeyer@gmail.com
#
# Changelog

# Description


# standard imports
#from operator import itemgetter, attrgetter
import os
#import pprint
import sys
import getopt
#from datetime import datetime
#from time import mktime
import BaseHTTPServer
import simplejson as json
from urlparse import urlparse, parse_qs
from subprocess import Popen
from subprocess import PIPE
import re
from os import curdir, sep


####################
# Global Variables

debug = 0
vernum = "0.1"
verbose = False
webserver = False


#########


# Print version information and exit
def version():
    print "+----------------------------------------------------------------------+"
    print "| Unanomaly Version "+ vernum +"                                                |"
    print "| This program is free software; you can redistribute it and/or modify |"
    print "| it under the terms of the GNU General Public License as published by |"
    print "| the Free Software Foundation; either version 2 of the License, or    |"
    print "| (at your option) any later version.                                  |"
    print "|                                                                      |"
    print "|  Authors                                                             |"
    print "|  Sebastian Garcia, eldraco@gmail.com                                 |"
    print "|  Maximo Martinez, maximomrtnz@gmail.com                              |"
    print "|  Pablo Meyer, pablitomeyer@gmail.com                                 |"
    print "+----------------------------------------------------------------------+"
    print


# Print help information and exit:
def usage():
    print "+----------------------------------------------------------------------+"
    print "| Unanomaly Version "+ vernum +"                                                |"
    print "| This program is free software; you can redistribute it and/or modify |"
    print "| it under the terms of the GNU General Public License as published by |"
    print "| the Free Software Foundation; either version 2 of the License, or    |"
    print "| (at your option) any later version.                                  |"
    print "|                                                                      |"
    print "|  Authors                                                             |"
    print "|  Sebastian Garcia, eldraco@gmail.com                                 |"
    print "|  Maximo Martinez, maximomrtnz@gmail.com                              |"
    print "|  Pablo Meyer, pablitomeyer@gmail.com                                 |"
    print "+----------------------------------------------------------------------+"
    print "\nusage: %s <options>" % sys.argv[0]
    print "options:"
    print "  -h, --help           Show this help message and exit"
    print "  -V, --version        Output version information and exit"
    print "  -v, --verbose        Output more information."
    print "  -D, --debug          Debug. In debug mode the statistics run live."
    print "  -f, --file           Dataset file to analyze."
    print "  -a, --anomalies      The maximum amount of anomalies that you want."
    print "  -p, --port           Webserver port"
    print "  -w, --webserver      Use the Webserver"
    print
    sys.exit(1)


def createWebServer(port):
    """ Crate a web server """
    global debug
    # By default bind to localhost
    server_address = ('127.0.0.1', port)

    # Create a webserver
    try:
        httpd = BaseHTTPServer.HTTPServer(server_address, MyHandler)
        # Get the socket
        sa = httpd.socket.getsockname()

        print "Serving HTTP on http://" + sa[0] + ":" + str(sa[1])

        # Run forever
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ' Received, shutting down the server.'
        httpd.socket.close()




class MyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    """ Handle the requests """

    def log_message(self, format, *args):
        return

    def do_GET(self):
        global debug
        note = ""
        alarm_type = ""
        try:
            if debug:
                print ' >> Path: {0}'.format(self.path)

            # Return the basic info about the MACs since last request
            # Get a MAC and add a note in the database 
            # /compute?file=test.csv&threshold=0.0001
            if self.path.rfind('/compute?file=') == 0: # and self.path.find("note=") > 0:
                if debug:
                    print ' >> Get /compute'
		

                parameters = parse_qs(urlparse(self.path).query)
		if debug:
		    print 'Params: {0}'.format(parameters)
                    
                #file = str(self.path.split('file=')[1].split('&')[0])
                #threshold = str(self.path.split('threshold=')[1])

                if debug:
                    print 'Web parameters: {0}'.format(parameters)
                file = parameters['file'][0]
                anomalies = parameters['anomalies'][0]

                json_to_send = compute_anomaly(file, anomalies)

                if json_to_send == '':
                    self.send_response(404)
                else:
                    self.send_response(200)
                self.send_header('Content-Type',        'text/html')
                self.end_headers()
                self.wfile.write(json_to_send)


            elif self.path != "/":
                # Read files in the directory
                if debug:
                    print ' >> Get generic file'

                try:
                    extension = self.path.split('.')[-1]
                    if len(extension.split('?')) >= 2:
                        extension = self.path.split('.')[-1].split('?')[0]
                        self.path = self.path.split('?')[0]
                except:
                    # Does not have . on it...
                    self.send_response(200)
                    return

                self.send_response(200)

                if extension == 'css':
                    file = open(curdir + sep + self.path)
                    temp_read = file.read()
                    file_len = len(temp_read)
                    self.send_header('Content-Type','text/css')
                    self.send_header('Content-Length',file_len)
                    self.end_headers()

                elif extension == 'png':
                    file = open(curdir + sep + self.path)
                    temp_read = file.read()
                    file_len = len(temp_read)
                    self.send_header('Content-Type','image/png')
                    self.send_header('Content-Length',file_len)
                    self.end_headers()

                elif extension == 'js':
                    file = open(curdir + sep + self.path)
                    temp_read = file.read()
                    file_len = len(temp_read)
                    self.send_header('Content-Type','text/javascript')
                    self.send_header('Content-Length', file_len)
                    self.end_headers()

                elif extension == 'html':
                    file = open(curdir + sep + self.path)
                    temp_read = file.read()
                    file_len = len(temp_read)
                    self.send_header('Content-Type','text/html; charset=UTF-8')
                    self.send_header('Content-Length',file_len)
                    self.end_headers()
                else:
                    self.send_header('Content-Type','text/html; charset=UTF-8')
                    self.send_header('Content-Length','9')
                    self.end_headers()
                    self.wfile.write('Hi there.')
                    return

                self.wfile.write(temp_read)
                file.close()

            return

        except IOError:
            self.send_error(404,'File Not Found: {0}'.format(self.path))



def verify_datafile(file):
    """ This function verifies the data in the file, looking for missing values or strings."""
    try:

        clean = True

        f = open(file)

        line = f.readline()

        # the first row is the boss
        amount_of_columns = len(line.split(','))

        while (line):
            if debug:
                print 'Line: {}'.format(line)

            # Verify that every line has the same amount of columns
            ac = len(line.split(','))
            if not ac == amount_of_columns:
                if debug:
                    print ' > Uneven number of columns in line: {}'.format(line)
                clean = False
                return clean

            # Verify that we only have numeric values
            #if not re.match('^[0-9,\.]+$',line):
            if not re.match('^[0-9,\.\-]+$',line):
                if debug:
                    print ' > Letters detected in line: {}'.format(line)
                    print ' > Only numbers are allowed! Check your file'
                clean = False
                return clean
            line = f.readline()

        return clean



    except Exception as inst:
        if debug:
            print 'Some problem in verify_datafile()'
        print type(inst)     # the exception instance
        print inst.args      # arguments stored in .args
        print inst           # __str__ allows args to printed directly
        x, y = inst          # __getitem__ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        exit(-1)


def compute_anomaly(file, anomalies):
    """ This function computes the anomaly value"""
    try:
        global debug
        global verbose
        global webserver

        je = json.JSONEncoder()
        anomalous_data = ""

        if debug:
            print 'Test file: {0}, anomalies: {1}'.format(file,anomalies)

        # Verify the dataset file
        if not verify_datafile(file):
            print 'There is an error in the file. Please check it'
            # Return an empty json so we can send an error to the web page.
            return ''


        # Octave command
        octave_command = ['/usr/bin/octave', '-q', 'test_anomaly.m', file, anomalies]
        if debug:
            print 'Command: {}'.format(octave_command)

        # Get the anomalous data
        try:
            anomalous_data = Popen(octave_command,stdout=PIPE).communicate()[0]
        except Exception as inst:
            if debug:
                print 'Some problem in Popen()'
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to printed directly
            x, y = inst          # __getitem__ allows args to be unpacked directly
            print 'x =', x
            print 'y =', y
            exit(-1)


        # Converto to json

        n_outliers = str(int(anomalous_data.split('\n')[0].split(':')[1]))
        lists = anomalous_data.split('\n')[1:-1]

        dict = {}
        dict['#Outliers'] = n_outliers
        dict['Lists'] = lists

        if (not webserver and verbose) or debug:
            print 'Number of outliers: {}'.format(dict['#Outliers'])
            print 'Outliers: {}'.format(dict['Lists'])
        elif not webserver:
            print 'Number of outliers: {}'.format(dict['#Outliers'])

        if webserver:
            if verbose:
                print 'Number of outliers: {}'.format(dict['#Outliers'])
            return je.encode(dict)
        else:
            print 'New number of anomalies (s to show the outliers values): ',
            n_anomalies = raw_input()
            if n_anomalies == 's':
                print 'Outliers: '
                for i in dict['Lists']:
                    print i
                compute_anomaly(file,anomalies)
            else:
                anomalies = n_anomalies
                compute_anomaly(file,anomalies)




    except Exception as inst:
        if debug:
            print 'Some problem in compute_anomaly()'
        print type(inst)     # the exception instance
        print inst.args      # arguments stored in .args
        print inst           # __str__ allows args to printed directly
        x, y = inst          # __getitem__ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        exit(-1)




def main():
    try:
        global debug
        global verbose
        global webserver

        file = ""
        anomalies = ""
        port = 8000
        webserver = ""

        opts, args = getopt.getopt(sys.argv[1:], "VvDhf:t:p:w", ["help","version","verbose","debug","file=","anomalies=", "port=", "webserver"])
    except getopt.GetoptError: usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"): usage()
        if opt in ("-V", "--version"): version() ; exit(-1)
        if opt in ("-v", "--verbose"): verbose = True
        if opt in ("-D", "--debug"): debug=1
        if opt in ("-f", "--file"): file = str(arg)
        if opt in ("-a", "--anomalies"): anomalies = str(arg)
        if opt in ("-p", "--port"): port = int(arg)
        if opt in ("-w", "--webserver"): webserver = True
    try:
        try:
            if file == "" and not webserver:
                usage()
                sys.exit(1)
            else:

                if webserver:
                    createWebServer(port)
                else:
                    compute_anomaly(file, anomalies)



        except Exception, e:
                print "misc. exception (runtime error from user callback?):", e
        except KeyboardInterrupt:
                sys.exit(1)


    except KeyboardInterrupt:
        # CTRL-C pretty handling.
        print "Keyboard Interruption!. Exiting."
        sys.exit(1)


if __name__ == '__main__':
    main()

