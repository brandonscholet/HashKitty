# HashcatHerder

Do you want to crack some files with out dealing with installing hashcat and drivers and then needing the paths for everything and all the arguments?

Have you never done password cracking and want to take a whack at it on easy mode?

HashcatHerder is a python wrapper to setup, install drivers, and run hashcat with ease.

It will with good defaults, but allow you you change what you neede without a bunch of path issues.

Once it is done with your wordlist is will recurse through your pots file passwords with rules until exausted and then print the results.

## Installation

```pip install .```

Follow any prompts to install drivers. IT should grab everything based on your cpu/arch. Let me know if I missed something!

## To run

```HashcatHerder -f dumped_creds ```

If the HashcatHerder binary causes issues use this. I'll leave it here for now

```./crack.py -f dumped_creds ```

## Wordlists, Rules

This tool downloads and sets as default the wordlist rockyou.txt and rule file oneruletorulethemallstill.rule

To use an alternate wordlist file use `-w <path to wordlist>`

to use the default rule file use `-r`

To use an alternate rule file use `-r <path to rules file>`

I recommend using [rockyou2021.txt](https://github.com/ohmybahgosh/RockYou2021.txt) +rules for cheap hashes.

## Modes

This will attempt `mode 1000 (NTLM)` cracking by default.

If you want it to try and guess the mode and use that use the flag `-a`

If you wish to specify a mode use `-m <mode>`

## Other Stuffs

`-q` is not done yet, but I wanted to quiet all the hashcat stuff and jsut spit out results, yaknow?
`-s` shows the cracked results that match and will NOT do any cracking. The summary is shown at the end anyways
`-u` if the username is in the dumped creds you will need to provide this


## Usage

!!!!Don't forget to use `-u` or `--user` if your creds file contains the usernames in the first column!!!!

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

## Roadmap
1. Spit out metrics for cracked passwords
2. Tell on high frequency password use as well as similarly named accounts with the same password.
3. allow you to push these cracker users into BH and mark them as owned, as well as add a custom edge for 
