#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from cookielib import MozillaCookieJar
from datetime import datetime
from getpass import getpass
from getopt import GetoptError, gnu_getopt
from hashlib import md5
from HTMLParser import HTMLParser
from json import load
from os import path, makedirs, getcwd, access, W_OK, X_OK
from sys import argv
from urllib import urlencode, unquote
from urllib2 import HTTPCookieProcessor, build_opener


class RDWorker:
    """
    Worker class to perform RealDebrid related actions:
    - format login info so they can be used by RealDebrid
    - login
    - unrestricting links
    - keeping cookies
    """

    _cookie_file = None
    _conf_file = None
    _endpoint = 'http://www.real-debrid.com/ajax/%s'

    cookies = None

    def __init__(self, cookie_file, conf_file):
        self._cookie_file = cookie_file
        self._conf_file = conf_file
        self.cookies = MozillaCookieJar(self._cookie_file)


    def ask_login(self):
        username = raw_input('What is your RealDebrid username?\n')
        raw_pass = getpass('What is your RealDebrid password (won\'t be displayed and won\'t be stored as plain text)?\n')
        password = md5(raw_pass).hexdigest()

        try:
            with open(self._conf_file, 'w') as file:
                file.write(username + ':' + password)
        except IOError as e:
            exit(str(e))

        return {'user': username, 'pass': password}


    def login(self, info):
        if path.isfile(self._cookie_file):
            self.cookies.load(self._cookie_file)

            for cookie in self.cookies:
                if cookie.name == 'auth' and not cookie.is_expired():
                        return # no need for a new cookie

        # request a new cookie if no valid cookie is found or if it's expired
        opener = build_opener(HTTPCookieProcessor(self.cookies))
        try:
            response = opener.open(self._endpoint % 'login.php?%s' % urlencode(info))
            resp = load(response)
            opener.close()

            if resp['error'] == 0:
                self.cookies.save(self._cookie_file)
            else:
                exit('Login failed: %s') % unicode(resp['message'])
        except Exception as e:
            exit('Login failed: %s' % str(e))


    def unrestrict(self, link):
        opener = build_opener(HTTPCookieProcessor(self.cookies))
        response = opener.open(self._endpoint % 'unrestrict.php?%s' % urlencode({'link': link}))
        resp = load(response)
        opener.close()

        if resp['error'] == 0:
            return resp['main_link']
        else:
            raise ValueError(resp['message'])


def usage(status = 0):
    """
    Print rdcli usage information
    """
    print 'Usage: rdcli [OPTIONS] LINK'

    print '\nOPTIONS:'
    print '  -q\tQuiet mode. No output will be generated.'
    print '  -t\tTest mode. Perform all operations EXCEPT file downloading.'
    print '  -i\tInit. Force rdcli to ask for your login and password.'
    print '\tUseful if you made a typo or if you changed your login information since you first used rdcli.'
    print '  -l\tList. Write a list of the successfully unrestricted links on STDOUT, without downloading.'
    print '\t-t and -q options have no effect if -l is used.'
    print '  -o\tOutput directory. Download files into a specific directory.'
    print '  -h\tHelp. Display this help.'

    print '\nLINK can be set of URLs to files you want to dowload (i.e. http://host.com/myFile.zip) or the path to a file containing them.'
    print '\nExample: rdcli http://host.com/myFile.zip'
    print 'Example: rdcli urls.txt'
    print 'Example: rdcli -t links-to-test.txt'

    print '\nReport rdcli bugs to https://github.com/MrMitch/realdebrid-CLI/issues/new'

    exit(status)


def main():
    """
    Main program
    """

    base = path.join(path.expanduser(u'~'), u'.config', 'rdcli-py')
    conf_file = path.join(base, 'rdcli.login')
    cookie_file = path.join(base, 'cookie.txt')

    list = False
    test = False
    verbose = True

    dir=getcwd()

    def debug(s):
        if verbose:
            print s,

    # make sure the config dir exists
    if not path.exists(base):
        makedirs(base)

    worker = RDWorker(cookie_file, conf_file)

    # parse command-line arguments
    try:
        opts, args = gnu_getopt(argv[1:], 'hiqtlo:')
    except GetoptError as e:
        print str(e)
        usage(1)

    for option, argument in opts:
        if option == '-h':
            usage()
        elif option == '-i':
            worker.ask_login()
        elif option == '-q':
            if not list:
                verbose = False
        elif option == '-t':
            if not list:
                test = True
        elif option == '-l':
            list = True
            test = False
            verbose = False
        elif option == '-o':
            dir = argument

    # no download and no output ? → better stop now
    if test and not verbose:
        exit(0)

    # make sure we have something to process
    if len(args) > 0 :
        # ensure we can write in output directory
        if not dir == getcwd() and not path.exists(unicode(dir)):
            debug('%s no such directory' % unicode(dir))
            exit(1)
        else:
            if not access(unicode(dir), W_OK | X_OK):
                debug('Output directory not writable')
                exit(1)
            else:
                dir = path.abspath(dir)
                debug('Output directory: %s\n' % dir)

        # retrieve login info
        try:
            with open(conf_file, 'r') as file:
                line = file.readline().split(':')
                info = {'user': line[0],'pass': line[1]}
        except IOError as e:
            info = worker.ask_login()

        # login
        try:
            worker.login(info)
        except Exception as e:
            exit('Login failed: %s' % str(e))

        if path.isfile(args[0]):
            with open(args[0], 'r') as f:
                links = f.readlines()
        else:
            links = args[0].splitlines()

        parser = HTMLParser()

        # unrestrict and download
        for link in links:
            link = link.strip()
            debug('Unrestricting %s' % link)

            try:
                unrestricted = worker.unrestrict(link)
                debug (u'→ ' + unrestricted + '\n')

                if list:
                    print unrestricted
                elif not test:
                    file = parser.unescape(unquote(path.basename(unrestricted)))
                    file = file.encode('latin-1').decode('utf-8').replace('/', '_')
                    fullpath = path.join(dir, file)

                    try:
                        opener = build_opener(HTTPCookieProcessor(worker.cookies))
                        stream = opener.open(unrestricted)
                        total_size = float(stream.info().getheaders('Content-Length')[0])

                        debug('Downloading: %s (%.2f MB)\n' % (fullpath, total_size/1048576))

                        downloaded_size = 0
                        with open(fullpath, 'wb') as output:
                            start = datetime.now()
                            while True:
                                buffer = stream.read(10240) #10 KB
                                if not buffer:
                                    end = datetime.now()
                                    break

                                output.write(buffer)
                                downloaded_size += len(buffer)

                                status = r'%d  [%3.2f%%]' % (downloaded_size, downloaded_size * 100. / total_size)
                                status += chr(8)*(len(status)+1)
                                debug(status)

                            stream.close()
                            debug('\nDownload completed in %s\n' % str(end - start).split('.')[0])
                    except Exception as e:
                        debug('Download failed: %s\n' % str(e))
            except Exception as e:
                debug ('WARNING: unrestriction failed (%s)' % unicode(e)+'\n')

        debug('End\n')
        return 0
    else:
        usage(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('^C caught, exiting...')
    except Exception as e:
        exit('Fatal error: %s' % str(e))