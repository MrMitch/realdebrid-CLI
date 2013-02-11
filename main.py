#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from getopt import GetoptError, gnu_getopt
from HTMLParser import HTMLParser
from os import path, makedirs, getcwd, access, W_OK, X_OK
from sys import argv
from RDWorker import RDWorker
from urllib import unquote
from urllib2 import HTTPCookieProcessor, build_opener


def usage(status=0):
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
    print '  -p\tPassword. Provide a password.'
    print '  -h\tHelp. Display this help.'

    print '\nLINK can be set of URLs to files you want to download (i.e. http://host.com/myFile.zip) ' \
          'or the path to a file containing them.'
    print '\nExample: rdcli http://host.com/myFile.zip'
    print 'Example: rdcli urls.txt'
    print 'Example: rdcli -t links-to-test.txt'

    print '\nReport rdcli bugs to https://github.com/MrMitch/realdebrid-CLI/issues/new'

    exit(status)


def main():
    """
    Main program
    """

    base = path.join(path.expanduser(u'~'), '.config', 'rdcli-py')
    conf_file = path.join(base, 'rdcli.login')
    cookie_file = path.join(base, 'cookie.txt')

    list = False
    test = False
    verbose = True

    password = ''
    dir = getcwd()

    def debug(s):
        if verbose:
            print s,

    # make sure the config dir exists
    if not path.exists(base):
        makedirs(base)

    worker = RDWorker(cookie_file, conf_file)

    # parse command-line arguments
    try:
        opts, args = gnu_getopt(argv[1:], 'hiqtlp:o:')
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
            dir = path.abspath(path.expanduser(argument))
        elif option == '-p':
            password = argument

    # no download and no output ? → better stop now
    if test and not verbose:
        exit(0)

    # make sure we have something to process
    if len(args) > 0:
        # ensure we can write in output directory
        if not dir == getcwd() and not path.exists(unicode(dir)):
            debug('%s no such directory' % unicode(dir))
            exit(1)
        else:
            if not access(unicode(dir), W_OK | X_OK):
                debug('Output directory not writable')
                exit(1)
            else:
                debug(u'Output directory: %s\n' % dir)

        # retrieve login info
        try:
            with open(conf_file, 'r') as conf:
                line = conf.readline().split(':')
                info = {'user': line[0], 'pass': line[1]}
        except IOError:
            try:
                info = worker.ask_login()
            except Exception as e:
                exit('Unable to get login info: %s' % str(e))

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
        MB = 1048576

        # unrestrict and download
        for link in links:
            link = link.strip()
            debug('\nUnrestricting %s' % link)

            try:
                unrestricted = worker.unrestrict(link, password)
                debug(u'→ ' + unrestricted + '\n')

                if list:
                    print unrestricted
                elif not test:
                    filename = parser.unescape(unquote(path.basename(unrestricted)))
                    filename = filename.encode('latin-1').decode('utf-8').replace('/', '_')
                    fullpath = path.join(dir, filename)

                    try:
                        opener = build_opener(HTTPCookieProcessor(worker.cookies))
                        stream = opener.open(unrestricted)
                        total_size = float(stream.info().getheaders('Content-Length')[0])

                        debug(u'Downloading: %s (%.2f MB)\n' % (fullpath, total_size / MB))

                        downloaded_size = 0
                        percentage = 0
                        with open(fullpath, 'wb') as output:
                            start = datetime.now()
                            while True:
                                content = stream.read(10240)  # 10 KB
                                if not buffer:
                                    end = datetime.now()
                                    break

                                output.write(content)
                                downloaded_size += len(content)
                                percentage = downloaded_size * 100. / total_size

                                status = r'%d  [%3.2f%%]' % (downloaded_size, percentage)
                                status += chr(8) * (len(status) + 1)
                                debug(status)

                            stream.close()
                            speed = (downloaded_size / MB) / (end - start).total_seconds()
                            debug('%.2f%% downloaded in %s (~ %.2f MB/s)\n' % (percentage, str(end - start).split('.')[0], speed))

                    except Exception as e:
                        debug('Download failed: %s\n' % str(e))
            except Exception as e:
                debug('WARNING: unrestriction failed (%s)' % unicode(e) + '\n')

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