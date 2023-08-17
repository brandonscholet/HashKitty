# HashcatHerder
A wrapper to setup and run hashcat with ease.

## Installation

```pip install .```

## Help

No

## To run

```HashcatHerder -f dumped_creds ```

``` ./crack.py -f dumped_creds ```

## Usage

```
PS C:\Users\BrandonScholet\Desktop> HashcatHerder.exe  -h
usage: HashcatHerder [-h] -f FILE [-r [RULES]] [-u] [-s] [-q] [-w WORDLIST] [-m MODE | -a]

Hashcat automation script.

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to the dumped file.
  -r [RULES], --rules [RULES]
                        Allows you to run rules. defaults to OneRuleToRuleThemStill
  -u, --user            If your input has the user. then you need this
  -s, --show            Show cracked Results for file
  -q, --quiet           Experimental mode to only show the results and nothing else.
  -w WORDLIST, --wordlist WORDLIST
                        to supply a wordlist that is not rockyou.txt
  -m MODE, --mode MODE  Set custom mode. Default is 1000 for NTLM
  -a, --auto-mode       Let it try to figure out the hash mode.
```  
