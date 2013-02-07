#!/usr/bin/env python2
import urllib2

__author__ = 'MrMitch'

from getpass import getpass
from getopt import GetoptError, gnu_getopt
from hashlib import md5
from sys import argv, stdin
from os import path, makedirs, getcwd, access, W_OK, X_OK
import urllib, urllib2, cookielib, json

BASE = path.expanduser(u'~') + u'/.config/rdcli-py'
CONF_FILE = BASE + u'/rdcli.login'
COOKIE = BASE + u'/cookie.txt'


# Print rdcli usage information
def usage():
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

    exit()


class RDWorker:

    cookies = None
    base_URL = 'http://www.real-debrid.com/ajax/%s'
    debugFlag = False

    def __init__(self):
        self.cookies = cookielib.MozillaCookieJar(COOKIE)

    def ask_login(self):
        username = raw_input('What is your RealDebrid username?\n')
        raw_pass = getpass('What is your RealDebrid password (won\'t be displayed and won\'t be stored as plain text)?\n')
        password = md5(raw_pass).hexdigest()

        try:
            with open(CONF_FILE, 'w') as file:
                file.write(username + ':' + password)
        except IOError as e:
            exit(str(e))

        return {'user': username, 'pass': password}

    def login(self, info):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        response = opener.open(self.base_URL % 'login.php?%s' % urllib.urlencode(info))
        resp = json.load(response)
        opener.close()

        if resp['error'] == 0:
            self.cookies.save()
        else:
            exit('Login failed: %s') % unicode(resp['message'])


    def unrestrict(self, link):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        response = opener.open(self.base_URL % 'unrestrict.php?%s' % urllib.urlencode({'link': link}))
        resp = json.load(response)
        opener.close()

        if resp['error'] == 0:
            return resp['main_link']
        else:
            raise ValueError(resp['message'])



def main():

    def debug(s):
        if verbose:
            print s,

    # make sure the config dir exists
    if not path.exists(BASE):
        makedirs(BASE)

    rdcli = RDWorker()

    try:
        opts, args = gnu_getopt(argv[1:], 'hiqtlo:')
    except GetoptError as e:
        print str(e)
        usage()

    list = False
    test = False
    verbose = True
    dir=getcwd()

    for option, argument in opts:
        if option == '-h':
            usage()
        elif option == '-i':
            rdcli.ask_login()
        elif option == '-q':
            if not list:
                verbose = False
        elif option == '-t':
            if not list and verbose:
                test = True
        elif option == '-l':
            list = True
            test = False
            verbose = False
        elif option == '-o':
            dir = argument


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
                debug('Output directory: %s\n' % dir)

        # retrieve login info
        try:
            with open(CONF_FILE, 'r') as file:
                line = file.readline().split(':')
                info = {'user': line[0],'pass': line[1]}
        except IOError as e:
            info = rdcli.ask_login()

        # see if a cookie already exists, create one if not
        if path.isfile(COOKIE):
            rdcli.cookies.load(COOKIE)
            found = False

            for cookie in rdcli.cookies:
                if cookie.name == 'auth':
                    found = True
                    if cookie.is_expired():
                        debug('Previous cookie expired, getting a new one\n')
                        rdcli.login(info)
                    else:
                        debug('Valid cookie\n')

            if not found:
                debug('No valid cookie found, login in\n')
                rdcli.login(info)

        else:
            debug('No previous cookie, login in')
            rdcli.login(info)

        if path.isfile(args[0]):
            with open(args[0], 'r') as f:
                links = f.readlines()
        else:
            links = args[0].splitlines()

        # unrestrict and download
        for link in links:
            debug('Unrestricting %s' % link)

            try:
                unrestricted = rdcli.unrestrict(link)
                debug ('-> ' + unrestricted + '\n')

                if list:
                    print unrestricted
                else:
                    file = path.join(dir, urllib.unquote_plus(unrestricted.split('/')[-1]))

                    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(rdcli.cookies))
                    stream = opener.open(unrestricted)
                    meta = stream.info()
                    total_size = float(meta.getheaders('Content-Length')[0])

                    print 'Downloading: %s (%.2f MB)' % (file, total_size/1048576)

                    downloaded_size = 0
                    block_size = 10240
                    output = open(file, 'wb')

                    while True:
                        buffer = stream.read(block_size)
                        if not buffer:
                            break

                        output.write(buffer)

                        downloaded_size += len(buffer)
                        status = r'%10d  [%3.2f%%]' % (downloaded_size, downloaded_size * 100. / total_size)
                        status += chr(8)*(len(status)+1)
                        debug(status)

                    output.close()
                    stream.close()

            except ValueError as e:
                debug ('WARNING: unrestriction failed (%s)' % unicode(e)+'\n')


    return 0

if __name__ == '__main__':

    main()