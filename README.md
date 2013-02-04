#realdebrid-CLI

Use Read-Debrid from your command line !

##Usage

```bash
mitch@raspberrypi ~ $ ./rdcli [OPTIONS] LINK
```

`OPTIONS` can be: 
```
-q    Quiet mode. No output will be generated.
-t    Test mode. Perform all operations EXCEPT file downloading.
-i    Init. Forces rdcli to ask for your login and password.
      Useful if you made a typo or if you changed your login information since you first used rdcli.
-h    Help. Display this help.
```

`LINK` can be a URL to a single file you want to dowload (i.e. `http://host.com/myFile.zip`) or a file containing several links.

##Examples:  

```bash
mitch@raspberrypi ~ $ ./rdcli http://host.com/myFile.zip  
mitch@raspberrypi ~ $ ./rdcli urls.txt
mitch@raspberrypi ~ $ ./rdcli -t links-to-test.txt`  
```

##License

This sofware is distributed under the [WTF Public License](http://www.wtfpl.net/). A copy of the license can be found [here](http://www.wtfpl.net/txt/copying).


##Contributing

This script was initially written for my personal use but I'd be more than happy if it could be useful to any folk from the magical land of the Internet. Feel free to fork and submit your Pull Request to fix/improve `rdcli`.

Report `rdcli` bugs [here](https://github.com/MrMitch/realdebrid-CLI/issues/new)
