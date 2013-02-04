#realdebrid-CLI

Use Read-Debrid from your command line !

##Usage

```bash
```

###OPTIONS:
  -q	Quiet mode. No output will be generated.
  -t	Test mode. Perform all operations EXCEPT file downloading.
  -i	Init. Forces rdcli to ask for your login and password.
	(useful if you made a typo or if you changed your login information since you first used rdcli).
  -h	Help. Display this help.

LINK can be a URL to the file you want to dowload (i.e. http://host.com/myFile.zip) or a file containing several links.

Example: ./rdcli http://host.com/myFile.zip
Example: ./rdcli urls.txt
Example: ./rdcli -t links-to-test.txt

Report rdcli bugs to https://github.com/MrMitch/realdebrid-CLI/issues/new
