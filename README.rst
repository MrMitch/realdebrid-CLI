`realdebrid-CLI`_ |version|
===========================

    Use Read-Debrid from your command line !

``rdcli`` is a tool allowing you to use Real-Debrid from your command
line. It’s written in `Python 2.7`_ because Python comes pre-installed
on most distribution nowadays, limiting the amount of software
dependency.

Installation
------------

Using ``pip`` (preferred method)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the latest version of ``rdcli`` on your computer, open a
terminal and enter the following line:

.. code:: bash

    sudo pip install rdcli

To update ``rdcli``, run :

.. code:: bash

    sudo pip install rdcli -U

Alternative method
~~~~~~~~~~~~~~~~~~

If you don’t have/want ``pip`` installed on your computer, you can
manually install ``rdcli`` with the following commands (cloning the repo
and launching the ``setup.py``)

.. code:: bash

    git clone https://github.com/MrMitch/realdebrid-CLI.git
    cd realdebrid-CLI
    python setup.py install

Usage
-----

In the command line
~~~~~~~~~~~~~~~~~~~

.. code:: bash

    mitch@raspberrypi ~ $ rdcli [OPTIONS] LINK

``OPTIONS`` can be:

::

    -h    Help. Display this help.
    -i    Init. Force rdcli to ask for your login and password.
          Useful if you made a typo or if you changed your login information since you first used rdcli.
    -l    List. Write a list of the successfully unrestricted links on STDOUT, without downloading.
          -t and -q options have no effect if -l is used.
    -o    Output directory. Download files into a specific directory.
    -O    Output file. Specify a name for the downloaded file instead of using the original file's name.
          -O has no effect if several files will be downloaded.
    -p    Password. Provide a password for protected downloads.
    -q    Quiet mode. No output will be generated.
    -t    Test mode. Perform all operations EXCEPT file downloading.

``LINK`` can be the URL to a file you want to download
(i.e. http://host.com/myFile.zip) or the path to a file containing one
ore several URL(s).

**Examples:**

.. code:: bash

    mitch@raspberrypi ~ $ rdcli http://host.com/myFile.zip
    mitch@raspberrypi ~ $ rdcli -o Documents/ http://host.com/myFile.zip
    mitch@raspberrypi ~ $ rdcli urls.txt
    mitch@raspberrypi ~ $ rdcli -t links-to-test.txt
    mitch@raspberrypi ~ $ rdcli -l links.txt > unrestricted-links.txt

For development purposes
~~~~~~~~~~~~~~~~~~~~~~~~

See the `RDWorker`_ file. It defines 4 classes:

-  ``RDError``: Base Exception to be inherited for all Exception related
   to Real-Debrid
-  ``UnrestrictionError``: Exception thrown when an error occurs during
   link unrestriction
-  ``LoginError``: Exception thrown when an error occurs on loging
-  ``RDWorker``: Worker class providing methods to

   -  login into Real-Debrid, establishing a cookie and keeping it until
      it’s expired
   -  unrestrict any supported link

License
-------

This software is distributed under the MIT License. A copy of
the license can be found in the `LICENSE.txt`_ file.

Contributing
------------

This script was initially written for my personal use but I’d be more
than happy if it could be useful to any folk from the magical land of
the Internet. Feel free to fork and submit your Pull Request to
fix/improve ``rdcli``.

Report ``rdcli`` bugs on
`github <https://github.com/MrMitch/realdebrid-CLI/issues/new>`__

Contributors
------------

| `MrMitch`_
| `fklingler`_

.. _realdebrid-CLI: https://github.com/MrMitch/realdebrid-CLI
.. _Python 2.7: http://docs.python.org/2/
.. _RDWorker: https://github.com/MrMitch/realdebrid-CLI/blob/master/rdcli/RDWorker.py
.. _LICENSE.txt: https://github.com/MrMitch/realdebrid-CLI/blob/master/LICENSE.txt
.. _MrMitch: http://github.com/MrMitch
.. _fklingler: http://github.com/fklingler
.. |version| image:: https://img.shields.io/pypi/v/rdcli.png