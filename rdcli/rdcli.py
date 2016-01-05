#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Command line utility named `rdcli`
"""

from datetime import datetime
import config
from getopt import GetoptError, gnu_getopt
from json import load
from os import path, makedirs, getcwd, access, W_OK, X_OK
from sys import argv
from config import VERSION
from RDWorker import RDWorker, UnrestrictionError
from urllib2 import HTTPCookieProcessor, build_opener


def print_version():
    print 'rdcli %s' % VERSION


def print_help():
    """
    Print rdcli usage information
    """
    print_version()

    print 'Usage: rdcli [OPTIONS] LINK'
    print '       rdcli --config OPTION_NAME NEW_VALUE'

    print '\nOPTIONS:'
    print '  -h\tHelp. Display this help.'
    print '  -i\tInit. Force rdcli to ask for your login and password.'
    print '\tUseful if you made a typo or if you changed your login information since you first used rdcli.'
    print '  -l\tList. Write a list of the successfully unrestricted links on STDOUT, without downloading.'
    print '\t-t and -q options have no effect if -l is used.'
    print '  -o\tOutput directory. Download files into a specific directory.'
    print '  -O\tOutput file. Specify a name for the downloaded file instead of using the original file\'s name.'
    print '\t-O has no effect if several files will be downloaded.'
    print '  -p\tPassword. Provide a password for protected downloads.'
    print '  -q\tQuiet mode. No output will be generated.'
    print '  -t\tTest mode. Perform all operations EXCEPT file downloading.'
    # print '  -T\tTimeout. The maximum number of seconds to wait for a download to start.'

    print '\n`LINK` can be the URL to a file you want to download (i.e. http://host.com/myFile.zip) or the path to a ' \
          'file containing one ore several URL(s).'

    print '\nExample: rdcli http://host.com/myFile.zip'
    print 'Example: rdcli urls.txt'
    print 'Example: rdcli -t links-to-test.txt'

    print '\nReport rdcli bugs to https://github.com/MrMitch/realdebrid-CLI/issues/new'


def main():
    """
    Main program
    """

    base = path.join(path.expanduser('~'), '.config', 'rdcli-py')
    conf_file = path.join(base, 'conf.json')
    cookie_file = path.join(base, 'cookie.txt')

    list_only = False
    test = False
    verbose = True
    timeout = 120

    # make sure the config dir exists
    if not path.exists(base):
        makedirs(base)

    try:
        with open(conf_file, 'r') as conf:
            configuration = load(conf)
    except (IOError, ValueError):
        configuration = {}

    # the default output dir is taken from the config file
    # if it hasn't been configured, then use the current directory
    output_dir = configuration.get('output_dir', getcwd())
    download_password = ''

    worker = RDWorker(cookie_file)

    # parse command-line arguments
    try:
        opts, args = gnu_getopt(argv[1:], 'hviqtlp:o:T:O:', ['config', 'version'])
    except GetoptError as e:
        print str(e)
        print_help()
        exit(1)

    for option, argument in opts:
        if option == '-h':
            print_help()
            exit(0)
        if option == '--version' or option == '-v':
            print_version()
            exit(0)
        if option == '--config':
            config_args = argv[2:]

            if len(config_args) == 0:
                print 'Error: No configuration option supplied'
                exit(1)
            if len(config_args) == 1:
                config_args.append(None)

            if len(config_args) > 2:
                print 'WARNING: the following values have been ignored:', ', '.join(config_args[2:])
                config_args = config_args[0:2]

            config.update_value(*config_args, conf_file=conf_file)
            exit(0)
        elif option == '-i':
            username, password = config.ask_credentials()
            config.save_credentials(username, password, conf_file)
        elif option == '-q':
            if not list_only:
                verbose = False
        elif option == '-t':
            if not list_only:
                test = True
        elif option == '-l':
            list_only = True
            test = False
            verbose = False
        elif option == '-o':
            output_dir = argument
        elif option == '-p':
            download_password = argument
        elif option == '-T':
            timeout = int(argument)
        elif option == '-O':
            filename = argument

    # stop now if no download and no output wanted
    if test and not verbose:
        exit(0)

    if verbose:
        def debug(s):
            print s,
    else:
        def debug(s):
            pass

    # make sure we have something to process
    if len(args) > 0:
        output_dir = path.abspath(path.expanduser(output_dir))
        # ensure we can write in output directory
        if not output_dir == getcwd() and not path.exists(unicode(output_dir)):
            debug('%s no such directory' % unicode(output_dir))
            exit(1)
        else:
            if not access(output_dir, W_OK | X_OK):
                debug('Output directory not writable')
                exit(1)
            else:
                debug(u'Output directory: %s\n' % output_dir)

        # retrieve login info
        try:
            with open(conf_file, 'r') as conf:
                configuration = load(conf)
                username = configuration.get('username', '')
                password = configuration.get('password', '')
        except (KeyError, IOError, ValueError):
            username, password = config.ask_credentials()
            config.save_credentials(username, password, conf_file)

        # login
        try:
            worker.login(username, password)
        except BaseException as e:
            exit('Login failed: %s' % str(e))

        if path.isfile(args[0]):
            with open(args[0], 'r') as f:
                links = f.readlines()
        else:
            links = args[0].splitlines()

        # unrestrict and download
        for link in links:
            link = link.strip()
            debug('\nUnrestricting %s' % link)

            try:
                unrestricted, original_filename = worker.unrestrict(link, download_password)
                debug(u' -> ' + unrestricted + '\n')

                if list_only:
                    print unrestricted
                elif not test:

                    if len(links) == 1:
                        try:
                            fullpath = path.join(output_dir, filename)
                        except NameError:
                            fullpath = path.join(output_dir, original_filename)
                    else:
                        fullpath = path.join(output_dir, original_filename)

                    try:
                        to_mb = lambda b: b / 1048576.
                        to_kb = lambda b: b / 1024.

                        opener = build_opener(HTTPCookieProcessor(worker.cookies))
                        stream = opener.open(unrestricted)
                        info = stream.info().getheaders('Content-Length')

                        total_size = 0
                        downloaded_size = 0

                        if len(info):
                            total_size = float(info[0])
                            start = 'Downloading: %s (%.2f MB)\n' % (fullpath, to_mb(total_size))
                        else:
                            start = 'Downloading: %s (unknown size)\n' % fullpath

                        debug(start)

                        with open(fullpath, 'wb') as output:
                            start = datetime.now()
                            end = datetime.now()

                            if verbose:
                                status = ''

                            while True:
                                try:
                                    content = stream.read(20480)  # 20 KB

                                    if not content:
                                        break

                                    output.write(content)
                                    downloaded_size += len(content)

                                    if verbose:
                                        padding_length = len(status)
                                        last_downloaded = len(content)

                                        if last_downloaded > 1024:
                                            speed = to_mb(last_downloaded) / (datetime.now() - end).total_seconds()
                                            unit = 'MB/s'
                                        else:
                                            speed = to_kb(last_downloaded) / (datetime.now() - end).total_seconds()
                                            unit = 'kB/s'

                                        status = '\r%.3f MB' % to_mb(downloaded_size)

                                        if total_size > 0:
                                            status += '  [%3.2f%%]' % (downloaded_size * 100. / total_size)

                                        status += '  @ %.2f %s' % (speed, unit)

                                        print status.ljust(padding_length),
                                        end = datetime.now()

                                except KeyboardInterrupt:
                                    break

                            output.flush()
                            stream.close()

                        speed = to_mb(downloaded_size) / (end - start).total_seconds()

                        if total_size > 0:
                            final_status = '%.2f MB [%.2f%%] downloaded in %s (%.2f MB/s avg.)' \
                                           % (to_mb(downloaded_size), (downloaded_size * 100. / total_size),
                                              str(end - start).split('.')[0], speed)
                        else:
                            final_status = '%.2f MB downloaded in %s (%.2f MB/s avg.)' \
                                           % (to_mb(downloaded_size), str(end - start).split('.')[0], speed)
                        debug('\r%s\n' % final_status)
                    except BaseException as e:
                        debug('\nDownload failed: %s\n' % e)
            except UnrestrictionError as e:
                debug('-> WARNING, unrestriction failed (%s)' % str(e) + '\n')

        debug('End\n')
        return 0
    else:
        print_help()
        exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('^C caught, exiting...')
