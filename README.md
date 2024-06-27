# HashKitty - Tame the cat!

HashKitty is a user-friendly Python wrapper designed to provide an easy hashcat experience for both beginners and experienced users.

This script simplifies the process of setting up, installing (including those pesky drivers), and running Hashcat for password cracking tasks. 

After HashKitty completes your cracking session, it will quuickly iterate through your previously cracked passwords, applying rules to exhaust all possible variations and nicely print the complete results.

Some hashtypes have advance analysis available, like NTLM.

## Installation

Before installing HashKitty, ensure you have [Python](https://www.python.org/downloads/) installed.

```pip install .```

Follow any prompts to install drivers. HashKitty should grab everything based on your cpu/arch, but let me know if I missed something!

## Basic Usage

```HashKitty -f dumped_creds ```

*Don't forget to use `-u` or `--user` if your creds file contains the usernames in the first column*

## Analysis and Reporting

Below are the current list of checks performed for select `hash types / modes`. Use `-a` or `--analysis` to switch to this mode

Please feel free to request or PR any additional checks as the data and prinitng is modular.

1. NTLM (1000):
- Not the Best Passwords
- Cracked Passwords for Enabled Users
- Cracked Passwords for all users
- Cracked Passwords for Status Unknown Users
- Cracked Passwords for Disabled Users
- Stale Passwords for enabled users ( age > 500 days)
- Cracked Hash Collisions
- Enabled User w/ Hash Collision
- Same user/hash check in multiple domains
- Similar user/hash in different domain
- Uncracked Hash Collisions
- Users with LM Hashes
- Blank Password Hash (Likely Disabled)
- Cracked Historical Passwords

### Writing new analysis:

Currently there is one set of data `user_data` with two other sets: `current_users` and `collisions`. 

The `current_users` is all the hashes in `user_data` that do not have `_history` in the name, if hashcat was pulled historically. 

`Collisions` is a set where a hash exists at least twice in the `user_data` data set.

### Exmaple analysis check for NTLM
```
    ############################################
    # Show Cracked Passwords For Enabled Users #
    ############################################
    #Specify title for tables/report            
    finding_title = "Cracked Passwords for Enabled Users"
    
    # Specify the desired order of columns
    column_order = ["user", "domain", "password", "user_status", "pwdLastSet"]

    # Define the array filter to exclude entries where 'password' is empty, no default has and user enabled
    array_filter = lambda x: x['password'] != '' and x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0" and x["user_status"] == "Enabled"

    # Define the sort order. "-" in front will do reverse order. The example below will sort by username then password, but lowercase
    sort_keys = [
	lambda x: x['user'].lower()
	lambda x: x['password'].lower(),

    ]

    # Call the printing function with the sample data, column order, filter, and sort key
    display_results(finding_title,current_users, column_order, array_filter, sort_keys)         
```



## Wordlists, Rules

By default, HashKitty downloads and uses the `rockyou.txt` wordlist and the `oneruletorulethemallstill.rule` rule file.

To use an alternate wordlist file use `-w <path to wordlist>`

to use the default rule file use `-r`

To use an alternate rule file use `-r <path to rules file>`

I recommend using [rockyou2021.txt](https://github.com/ohmybahgosh/RockYou2021.txt) + rules for computationally cheap hash types, or if time is no issue.

## Modes

HashKitty attempts to automatically determine the hash type by default (with a menu for multiple choices).

To specify a mode use `-m <mode>`

## Other Stuffs

- `-q` quiet all the hashcat stuff and just spit out results, yaknow?
- `-s` shows the cracked results that match but will NOT do any cracking. The summary is shown at the end anyways.
- `-u` if your creds file contains the usernames in the first column, you will need to include this flag


## Full Usage
```
usage: HashKitty [-h] -f FILE [-r [RULES]] [-u] [-s] [-q] [-w WORDLIST] [-d] [-m MODE] [-a]

Hashcat automation script.

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to the dumped file.
  -r [RULES], --rules [RULES]
                        Allows you to run rules. defaults to OneRuleToRuleThemStill
  -u, --user            If your input has the user. then you need this
  -s, --show            Show cracked Results for file
  -q, --quiet           show the results as they are creacked and nothing else from hashcat
  -w WORDLIST, --wordlist WORDLIST
                        to supply a wordlist that is not rockyou.txt
  -d, --disable         Disable self test if hashcat is being a pain.
  -m MODE, --mode MODE  Manually set hash type
  -a, --analysis        Findings Analysis for select hashtypes (NTLM)
```  

## Roadmap
1.  - Metrics 
	- [x]  Lots of checks
	- [ ]  More Checks
2. Reporting: 
    - [x]  most-commonly used passwords
    - [x]  similarly named accounts using identical passwords
    - [ ]  json,csv output of all data
    - [ ]  Scoring and Work Report?
3. BloodHound integration:
    - [ ]  send info about cracked users to BH and mark them as owned
    - [ ]  create custom edges
4. 
