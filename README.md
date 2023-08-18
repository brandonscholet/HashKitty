# HashcatHerder

- Do you want to crack some files without the hassle of installing hashcat and required GPU drivers?
- Are you new to cracking and want to take a whack at it on easy mode?
- Are you experienced with cracking but want to minimize some of the mental effort involved? (So many paths! So many arguments!)

HashcatHerder is a python wrapper to setup, install, and run hashcat with ease - including required drivers!

While HashcatHerder configures up hashcat with useful default settings, you can easily change settings without fighting against path issues.

Once HashcatHerder is done with your wordlist, it will recurse through your pots file passwords with rules until exhausted then print the results.

## Installation

```pip install .```

Follow any prompts to install drivers. HashcatHerder should grab everything based on your cpu/arch, but let me know if I missed something!

## To run

```HashcatHerder -f dumped_creds ```

If the HashcatHerder binary causes issues, you can run crack.py instead:

```./crack.py -f dumped_creds ```

## Wordlists, Rules

By default, HashcatHerder downloads and uses the wordlist rockyou.txt and rule file oneruletorulethemallstill.rule.

To use an alternate wordlist file use `-w <path to wordlist>`

to use the default rule file use `-r`

To use an alternate rule file use `-r <path to rules file>`

I recommend using [rockyou2021.txt](https://github.com/ohmybahgosh/RockYou2021.txt) + rules for cheap hashes.

## Modes

HashcatHerder attempts to use `mode 1000 (NTLM)` cracking by default, but it can also attempt to guess the mode by using the flag `-a`.

To specify a mode use `-m <mode>`.

## Other Stuffs

- `-q` is not done yet, but I wanted to quiet all the hashcat stuff and jsut spit out results, yaknow?
- `-s` shows the cracked results that match and will NOT do any cracking. The summary is shown at the end anyways
- `-u` if the username is in the dumped creds you will need to provide this


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
1. Metrics for cracked passwords
2. Reporting: 
    - most-commonly used passwords
    - similarly named accounts using identical passwords
3. BloodHound integration:
    - send info about cracked users to BH and mark them as owned
    - create custom edges
