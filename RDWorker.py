__author__ = 'MrMitch'

from cookielib import MozillaCookieJar
from getpass import getpass
from hashlib import md5
from json import load
from urllib import urlencode
from urllib2 import HTTPCookieProcessor, build_opener
from os import path


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
        raw_pass = getpass('What is your RealDebrid password '
                           '(won\'t be displayed and won\'t be stored as plain text)?\n')
        password = md5(raw_pass).hexdigest()

        try:
            with open(self._conf_file, 'w') as file:
                file.write(username + ':' + password)
        except IOError:
            raise

        return {'user': username, 'pass': password}

    def login(self, info):
        if path.isfile(self._cookie_file):
            self.cookies.load(self._cookie_file)

            for cookie in self.cookies:
                if cookie.name == 'auth' and not cookie.is_expired():
                    return  # no need for a new cookie

        # request a new cookie if no valid cookie is found or if it's expired
        opener = build_opener(HTTPCookieProcessor(self.cookies))
        try:
            response = opener.open(self._endpoint % 'login.php?%s' % urlencode(info))
            resp = load(response)
            opener.close()

            if resp['error'] == 0:
                self.cookies.save(self._cookie_file)
            else:
                raise Exception('Login error: %s' % unicode(resp['message']))
        except Exception as e:
            raise Exception('Login failed: %s' % str(e))

    def unrestrict(self, link, password=''):
        opener = build_opener(HTTPCookieProcessor(self.cookies))
        response = opener.open(self._endpoint % 'unrestrict.php?%s' % urlencode({'link': link, 'password': password}))
        resp = load(response)
        opener.close()

        if resp['error'] == 0:
            return resp['main_link']
        else:
            raise ValueError(resp['message'])