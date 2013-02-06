#!/usr/bin/env python2
import urllib2

__author__ = 'MrMitch'

from getpass import getpass
from getopt import getopt
from hashlib import md5
from sys import argv, stdin
from os import path, makedirs
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
    print '  -h\tHelp. Display this help.'

    print '\nLINK can be set of URLs to files you want to dowload (i.e. http://host.com/myFile.zip) or the path to a file containing them.'
    print '\nExample: rdcli http://host.com/myFile.zip'
    print 'Example: rdcli urls.txt'
    print 'Example: rdcli -t links-to-test.txt'

    print '\nReport rdcli bugs to https://github.com/MrMitch/realdebrid-CLI/issues/new'

    return


class RDWorker:

    cookies = None
    base_URL = 'http://www.real-debrid.com/ajax/%s'
    logged = False

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
            print e
            exit()

        return {'user': username, 'pass': password}

    def login(self, info):
        print 'No valid cookie, login in'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        response = opener.open(self.base_URL % 'login.php?%s' % urllib.urlencode(info))
        resp = json.load(response)

        print resp

        if resp['error'] == 0:
            self.cookies.save()
        else:
            exit('Login failed: %s') % resp['message']


    def unrestrict(self):
        return



def main(args):
    print args

    # make sure the config dir exists
    if not path.exists(BASE):
        makedirs(BASE)

    rdcli = RDWorker()

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
                    rdcli.login(info)

        if not found:
            rdcli.login(info)

    else:
        rdcli.login(info)



    return 0

if __name__ == '__main__':

    main(argv[1:])