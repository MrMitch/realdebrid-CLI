# -*- coding: utf-8 -*-
_author__ = 'MrMitch'

from cookielib import MozillaCookieJar
from HTMLParser import HTMLParser
from json import load
from urllib import unquote, urlencode
from urllib2 import build_opener, HTTPCookieProcessor
from urlparse import urlparse
from os import path


class RDError(Exception):
    """
    Base class for all Real-Debrid related exceptions
    """

    DEFAULT_CODE = -100

    def __init__(self, message, code=DEFAULT_CODE):
        self.message = message
        self.code = code

    def __str__(self):
        return '[Error %i] %s' % (self.code, self.message)


class UnrestrictionError(RDError):

    UNSUPPORTED = 4
    UPGRADE_NEEDED = 2
    NO_SERVER = 9
    UNAVAILABLE = 11

    @classmethod
    def fixable_errors(cls):
        """
        Get the set of errors that are not fatal
        :return:
        """
        return cls.UPGRADE_NEEDED, cls.NO_SERVER


class LoginError(RDError):

    MISSING_INFO = -1
    BAD_CREDENTIALS = 1
    TOO_MANY_ATTEMPTS = 3


class RDWorker:
    """
    Worker class to perform RealDebrid related actions:
    - format login info so they can be used by RealDebrid
    - login
    - unrestricting links
    - keeping cookies
    """

    _endpoint = 'http://www.real-debrid.com/ajax/%s'

    def __init__(self, cookie_file):
        self._cookie_file = cookie_file
        self.cookies = MozillaCookieJar(self._cookie_file)

    def login(self, username, password):
        """
        Log into Real-Debrid
        :param username:
        :param password:
        :return: :raise:
        """
        if path.isfile(self._cookie_file):
            self.cookies.load(self._cookie_file)

            for cookie in self.cookies:
                if cookie.name == 'auth' and not cookie.is_expired():
                    return  # no need for a new cookie

        # request a new cookie if no valid cookie is found or if it's expired
        opener = build_opener(HTTPCookieProcessor(self.cookies))
        try:
            response = opener.open(self._endpoint % 'login.php?%s' % urlencode({'user': username, 'pass': password}))
            resp = load(response)
            opener.close()

            if resp['error'] == 0:
                self.cookies.save(self._cookie_file)
            else:
                raise LoginError(resp['message'].encode('utf-8'), resp['error'])
        except Exception as e:
            raise Exception('Login failed: %s' % str(e))

    def unrestrict(self, link, password=''):
        """
        Unrestrict a download URL
        :param link:
        :param password:
        :return: :raise:
        """
        opener = build_opener(HTTPCookieProcessor(self.cookies))
        response = opener.open(self._endpoint % 'unrestrict.php?%s' % urlencode({'link': link, 'password': password}))
        resp = load(response)
        opener.close()

        if resp['error'] == 0:
            return resp['main_link'].encode('latin-1').decode('utf-8')
        else:
            raise UnrestrictionError(resp['message'].encode('utf-8'), resp['error'])

    def get_filename_from_url(self, original):
        """
        Extract and decode a filename from an unrestricted url
        :param original:
        :return:
        """
        parser = HTMLParser()
        filename = urlparse(original).path.split('/')[-1]
        filename = parser.unescape(unquote(filename))
        return filename.replace('/', '_')
