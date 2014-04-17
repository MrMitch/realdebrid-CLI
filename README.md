#[realdebrid-CLI](https://github.com/MrMitch/realdebrid-CLI)

> Use Read-Debrid from your command line !

`rdcli` is a tool allowing you to use RealDebrid from your command line.
It's written in ([Python 2.7](http://docs.python.org/2/)) because Python comes pre-installed on most distribution nowadays, limiting the amount of software dependency.

##Installation

###Using `pip` (prefered method)
To install the latest version of `rdcli` on your computer, open a terminal and enter the following line:
```bash
sudo pip install rdcli
```

To update `rdcli`, run :
```bash
sudo pip install rdcli -U
```

###Aternative method
If you don't have/want `pip` installed on your computer, you can manually install `rdcli` with the following commands (cloning the repo and launching the `setup.py`)
```bash
git clone https://github.com/MrMitch/realdebrid-CLI.git
cd realdebrid-CLI
python setup.py install
```

##Usage

###In the command line
```bash
mitch@raspberrypi ~ $ rdcli [OPTIONS] LINK
```

`OPTIONS` can be: 
```
-h    Help. Display this help.
-i    Init. Force rdcli to ask for your login and password.
      Useful if you made a typo or if you changed your login information since you first used rdcli.
-l    List. Write a list of the successfully unrestricted links on STDOUT, without downloading.
      -t and -q options have no effect if -l is used.
-o    Output directory. Download files into a specific directory.
-p    Password. Provide a password for protected downloads.
-q    Quiet mode. No output will be generated.
-t    Test mode. Perform all operations EXCEPT file downloading.
```

`LINK` can be the URL to a file you want to download (i.e. http://host.com/myFile.zip) or the path to a file containing one ore several URL(s).

**Examples:**  

```bash
mitch@raspberrypi ~ $ rdcli http://host.com/myFile.zip
mitch@raspberrypi ~ $ rdcli -o Documents/ http://host.com/myFile.zip
mitch@raspberrypi ~ $ rdcli urls.txt
mitch@raspberrypi ~ $ rdcli -t links-to-test.txt
mitch@raspberrypi ~ $ rdcli -l links.txt > unrestricted-links.txt
```

###For development purposes
See the [RDWorker](rdcli/RDWorker.py) file. It defines 4 classes: 

* `RDError`: Base Exception to be inherited for all Exception related to RealDebrid 
* `UnrestrictionError`: Exception thrown when an error occurs during link unrestriction
* `LoginError`: Exception thrown when an error occurs on loging
* `RDWorker`: Worker class providing methods to
    * login into RealDebrid, establishing a cookie and keeping it until it's expired
    * unrestrict any supported link



##License

This software is distributed under the [WTF Public License](http://www.wtfpl.net/). A copy of the license can be found [here](http://www.wtfpl.net/txt/copying).


##Contributing

This script was initially written for my personal use but I'd be more than happy if it could be useful to any folk from the magical land of the Internet. Feel free to fork and submit your Pull Request to fix/improve `rdcli`.

Report `rdcli` bugs [here](https://github.com/MrMitch/realdebrid-CLI/issues/new)

##Contributors

[MrMitch](http://github.com/MrMitch)  
[fklingler](http://github.com/fklingler)
