"""
    Python library to use Real-Debrid services :
    - login
    - link unrestriction

    Tested on python 2.7
"""

from RDWorker import RDWorker, RDError, UnrestrictionError, LoginError

__all__ = ['RDWorker', 'RDError', 'UnrestrictionError', 'LoginError']

__author__ = 'MrMitch'
__version__ = 0.7
