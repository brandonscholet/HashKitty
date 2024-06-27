import argparse
import requests
import os
import subprocess
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlretrieve
import platform
import sys
from collections import defaultdict, Counter
from tabulate import tabulate
import pandas as pd
from difflib import SequenceMatcher

import urllib3
urllib3.disable_warnings()

def get_gpu_brand():
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"]).decode('utf-8')
            if "NVIDIA" in output:
                return "NVIDIA"
            elif "AMD" in output or "Radeon" in output:
                return "AMD"
            else:
                return None
        except Exception as e:
            # print(f"Error: {e}")
            return None
    elif platform.system() == "Linux":
        try:
            output = subprocess.check_output(["lspci", "-nnk"]).decode('utf-8')
            if "NVIDIA" in output:
                return "NVIDIA"
            elif "AMD" in output or "Radeon" in output:
                return "AMD"
            else:
                return None
        except Exception as e:
            # print(f"Error: {e}")
            return None
    else:
        print("GPU: This script only supports Windows and Linux.")
        return None

def get_cpu_brand():
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(["wmic", "cpu", "get", "name"]).decode('utf-8')
            if "Intel" in output:
                return "Intel"
            else:
                return None
        except Exception as e:
            # print(f"Error: {e}")
            return None
    elif platform.system() == "Linux":
        try:
            output = subprocess.check_output(["lscpu"]).decode('utf-8')
            if "Intel" in output:
                return "Intel"
            else:
                return None
        except Exception as e:
            # print(f"Error: {e}")
            return None
    else:
        print("CPU: This script only supports Windows and Linux.")
        return None

def check_AMD_drivers():
    if platform.system() == "Windows":
        verify_install = "driverquery /v /nh"

        AMD_driver_found = False
        x = subprocess.run(verify_install, stdout=subprocess.PIPE, universal_newlines=True)
        lines = x.stdout.split('\n')
        for line in lines:
            if "Adrenalin" in line:
                AMD_driver_found = True
                print("AMD Drivers installed")
                
        if not AMD_driver_found:
            print("AMD Drivers not installed")
            url = "https://www.amd.com/en/support"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
            }

            response = requests.get(url, headers=headers, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')

            download_link = None

            for a in soup.find_all('a'):
                if a.text == "Download Now":
                    download_link = a['href']
                    break
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', 
                "Referer": "https://www.amd.com/"
            }
            response = requests.get(download_link, headers=headers, verify=False)
            
            exe_name = "amd_installer.exe"
            
            with open(exe_name, "wb") as exe_file:
                exe_file.write(response.content)

            print(f"{exe_name} downloaded. Starting installation...")
            os.system(f"start {exe_name}")
            
            AMD_driver_found = False
            x = subprocess.run(verify_install, stdout=subprocess.PIPE, universal_newlines=True)
            lines = x.stdout.split('\n')
            for line in lines:
                if "Adrenalin" in line:
                    AMD_driver_found = True
                    print("AMD Drivers installed")
            
            if not AMD_driver_found:
                print("AMD Driver install failed. Exiting")
                exit()
    elif platform.system() == "Linux":
        try:
            output = subprocess.check_output(["dpkg-query", "-l", "amdgpu"]).decode('utf-8')
            if "amdgpu" in output:
                print("AMD Drivers installed")
            else:
                print("AMD Drivers not installed")
        except subprocess.CalledProcessError:
            print("AMD Drivers not installed. Please install the AMDGPU driver.")
        except Exception as e:
            # print(f"Error: {e}")
            pass

def check_Cuda_drivers():
    if platform.system() == "Windows" or platform.system() == "Linux":
        verify_install = "nvcc --version"

        try:
            subprocess.run(verify_install, stdout=subprocess.PIPE)
        except:
            print("Cuda Drivers not installed. Please install latest version")
            if platform.system() == "Windows":
                os.system("start https://developer.nvidia.com/cuda-downloads")
            elif platform.system() == "Linux":
                os.system("xdg-open https://developer.nvidia.com/cuda-downloads")
            exit()
    else:
        print("Cuda: This script only supports Windows and Linux.")
        return
  
def check_NVIDIA_drivers():
    if platform.system() == "Windows":
        verify_install = "nvidia-smi --query-gpu=driver_version --format=csv,noheader"
        try:
            driver_version = subprocess.check_output(verify_install.split(" "))
            driver_version = float(driver_version)
            if driver_version > 440.64:
                return
        except:
            pass
            
        verify_install = '''wmic path win32_VideoController get Name'''
        wmic_output = subprocess.run(verify_install, stdout=subprocess.PIPE, universal_newlines=True)
        device_names = wmic_output.stdout.split('\n')
        for device in device_names:
            if "NVIDIA" in device:
                print(f"Issue finding appropriate NVIDIA Driver. Download correct version (>440) for \"{device.strip()}\"")
                os.system("start https://www.nvidia.com/Download/index.aspx")
        exit()
    elif platform.system() == "Linux":
        verify_install = "nvidia-smi --query-gpu=driver_version --format=csv,noheader"
        try:
            driver_version = subprocess.check_output(verify_install.split(" ")).decode('utf-8').strip()
            driver_version = float(driver_version)
            if driver_version > 440.64:
                return
        except:
            print("Issue finding appropriate NVIDIA Driver. Download the correct version (>440)")
            os.system("xdg-open https://www.nvidia.com/Download/index.aspx")
            exit()
    else:
        print("NVIDIA: This script only supports Windows and Linux.")
        return

def check_Intel_OpenCL_drivers(hashcat_folder):
    os.chdir(hashcat_folder)
    verify_install = "hashcat -I"
    try:
        output = subprocess.check_output(verify_install.split(" ")).decode('utf-8')
        pattern = re.compile(r'Intel.*OpenCL')
        match = pattern.search(output)
        if match:
            return
    except:
        print("Intel OpenCL not detected by hashcat. Please install the latest version of OpenCL Runtime for Intel Core and Intel Xeon Processors")
        if platform.system() == "Windows":
            os.system("start https://www.intel.com/content/www/us/en/developer/tools/opencl-cpu-runtime/overview.html")
        elif platform.system() == "Linux":
            os.system("xdg-open https://www.intel.com/content/www/us/en/developer/tools/opencl-cpu-runtime/overview.html")
        exit()
    else:
        return

def check_drivers(hashcat_folder):
    gpu_brand = get_gpu_brand()
    cpu_brand = get_cpu_brand()

    if not gpu_brand:
        print("GPU not detected or unsupported.")

    if not cpu_brand:
        print("CPU not detected or unsupported.")
    if gpu_brand == "AMD":
        check_AMD_drivers()
    elif gpu_brand == "NVIDIA":
        check_Cuda_drivers()
        check_NVIDIA_drivers()
    if cpu_brand == "Intel":
        check_Intel_OpenCL_drivers(hashcat_folder)

def prereq_setup():
    url = 'https://hashcat.net/hashcat/'
    response = requests.get(url, verify=False)
    content = response.content

    soup = BeautifulSoup(content, 'html.parser')
    version_div = soup.select_one('#download table tr td a')['href']

    file_url = urljoin(url, version_div)
    version = re.search(r'hashcat-(\d+\.\d+\.\d+)', file_url).group(1)

    if platform.system() == "Windows":
        hashcat_root_dir = "C:\\hashcat"
        hashcat_results_folder = "C:\\hashcat"
        seven_zip_executable = "C:\\Program Files\\7-Zip\\7z.exe"
    elif platform.system() == "Linux":
        hashcat_root_dir = "/opt/hashcat"
        hashcat_results_folder = os.path.expanduser("~")+"/.hashcat/"
        seven_zip_executable = "/usr/bin/7z"

    os.makedirs(hashcat_root_dir, exist_ok=True)
    os.makedirs(hashcat_results_folder, exist_ok=True)

    hashcat_folder = os.path.join(hashcat_root_dir, f"hashcat-{version}")
    
    if not os.path.exists(hashcat_results_folder):
        os.makedirs(hashcat_results_folder)
        
    empty_file = os.path.join(hashcat_results_folder, "empty.txt")


    with open(empty_file, "w") as file:
        pass

    if not os.path.exists(hashcat_folder):
        print(f"Current Hashcat version: {version}")

        urlretrieve(file_url, "hashcat.7z")
        print("Downloaded hashcat.7z")

        subprocess.run([seven_zip_executable, "x", "-y", "-o" + hashcat_root_dir, "hashcat.7z"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Unzipped hashcat.7z to {hashcat_root_dir}")

        os.remove("hashcat.7z")
        print("Cleaned up downloaded file")

        os.chdir(hashcat_folder)

        test_run = subprocess.run(["hashcat", "-b", "-m", "1000", "-O", "-D", "1,2,3", "-w", "4"])
        if test_run.returncode != 0:
            raise Exception(f"Hashcat benchmark failed with return code: {test_run.returncode}")
            exit()
    else:
        hashcat_folder = os.path.join(hashcat_root_dir, f"hashcat-{version}")
        os.chdir(hashcat_folder)
        
        
    os.chdir(hashcat_results_folder)
    
    rockyou_file = os.path.join(hashcat_results_folder, "rockyou.txt")
    if not os.path.exists(rockyou_file):
        urlretrieve('https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt', rockyou_file)
        print(f"Downloaded rockyou.txt")

    one_rule_file = os.path.join(hashcat_results_folder, "OneRuleToRuleThemStill.rule")
    if not os.path.exists(one_rule_file):
        urlretrieve('https://raw.githubusercontent.com/stealthsploit/OneRuleToRuleThemStill/main/OneRuleToRuleThemStill.rule', one_rule_file)
        print(f"Downloaded OneRuleToRuleThemStill.rule")

    return hashcat_folder, hashcat_results_folder

def validate_file(f):
    if not os.path.exists(f):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return os.path.abspath(f).replace('\\', '/')

def parse_hash_file(file_path,user_data,final_mode):
    with open(file_path, 'r') as file:
        file_data = file.readlines()
        for line in file_data:
            parts = line.strip().split(":")
            
            if len(parts) >= 4:
                password=""
                #pwdLastSet = ""
                history_user=False
                domain_user = parts[0]
                password_hash = parts[3]   
                user_status_match = re.search(r'\(status=(Enabled|Disabled)\)', line)
                user_status = user_status_match.group(1) if user_status_match else "Unknown"

                pwd_set_match = re.search(rf'\(pwdLastSet=([\d-]*)', line)
                pwdLastSet = pwd_set_match.group(1) if pwd_set_match else ""
                
                if "\\" in domain_user:
                    domain, username = domain_user.split("\\")
                else:
                    domain, username = "", domain_user
                
                
                if "_history" in username:
                    history_user = username.split("_history")[1]
                else:
                    history_user=False                    
                                     
                    
                if final_mode==str(1000):
                    lm_hash = parts[2]
                    password_hash = parts[3]
                    
                    user_data.append({"user": username, "domain": domain, "lm_hash": lm_hash, "password_hash": password_hash, "user_status": user_status, "password": password, "pwdLastSet": pwdLastSet, "history_user": history_user })
                else:
                    password_hash = parts[3]
                    user_data.append({"user": username, "domain": domain, "password_hash": password_hash, "user_status": user_status, "password": password, "pwdLastSet": pwdLastSet, "history_user": history_user })
                    
def parse_hash_file(file_path,user_data,final_mode):
    with open(file_path, 'r') as file:
        file_data = file.readlines()
        for line in file_data:
            parts = line.strip().split(":")
            
            if len(parts) >= 4:
                password=""
                #pwdLastSet = ""
                history_user=False
                domain_user = parts[0]
                password_hash = parts[3]   
                user_status_match = re.search(r'\(status=(Enabled|Disabled)\)', line)
                user_status = user_status_match.group(1) if user_status_match else "Unknown"

                pwd_set_match = re.search(rf'\(pwdLastSet=([\d-]*)', line)
                pwdLastSet = pwd_set_match.group(1) if pwd_set_match else ""
                
                if "\\" in domain_user:
                    domain, username = domain_user.split("\\")
                else:
                    domain, username = "", domain_user
                
                
                if "_history" in username:
                    history_user = username.split("_history")[1]
                else:
                    history_user=False                    
                                     
                    
                if final_mode==str(1000):
                    lm_hash = parts[2]
                    password_hash = parts[3]
                    
                    user_data.append({"user": username, "domain": domain, "lm_hash": lm_hash, "password_hash": password_hash, "user_status": user_status, "password": password, "pwdLastSet": pwdLastSet, "history_user": history_user })
                else:
                    password_hash = parts[3]
                    user_data.append({"user": username, "domain": domain, "password_hash": password_hash, "user_status": user_status, "password": password, "pwdLastSet": pwdLastSet, "history_user": history_user })                    
          
"""def parse_hashcat(hashcat_data,user_data,final_mode):
    for line in hashcat_data:
        if "Failed" not in line:
            # Split the line by colon
            if ":" in line:
                parts = line.strip().split(':')
                
                if len(parts) == 3:
                    username, password_hash, password = parts
                    if "\\" in username:
                        domain, username = username.split('\\')
                    else: 
                        domain = ""
                           
                    if "_history" in username:
                        history_user = username.split("_history")[1]
                    else:
                        history_user=False
                    
                    for user in user_data:
                        if user["user"] == username and user["password_hash"]==password_hash and user["history_user"] == history_user:
                        
                            user["password"]=password
"""                            
                                                       
def parse_hashcat(hashcat_folder,hashcat_results_folder,user_data, final_mode):

    if platform.system() == "Windows":
        pot_file = os.path.join(hashcat_folder, "hashcat.potfile")
    else:
        pot_file = os.path.join(hashcat_results_folder, "hashcat.potfile")

    # Read new cracked passwords from pot file
    with open(pot_file, "r") as f:
        lines = f.readlines()

    cracked_hashes = set()
    for line in lines:
        columns = line.strip().split(":")
        password=columns[-1]
        cracked_hash=":".join(columns[:-1])
        
        for user in user_data:
            if user["password_hash"] == cracked_hash:
                user["password"] = password
                
    os.chdir(hashcat_results_folder)            

def display_results(finding_title,user_data, column_order, array_filter=None, sort_keys=None, sort_by_freq=None):
   

    # Apply filtering if an array_filter is provided
    if array_filter is not None:
        user_data = list(filter(array_filter, user_data))

    # Calculate frequencies if sort_by_freq is provided
    if sort_by_freq is not None:
        freq_counter = Counter(entry[sort_by_freq] for entry in user_data)
        sort_keys = [lambda x: freq_counter[x[sort_by_freq]]] + (sort_keys or [])
        # Sort the filtered data by frequency and other sort keys
        user_data = sorted(user_data, key=lambda x: tuple(key(x) for key in sort_keys), reverse=True)
    elif sort_keys is not None:
        sort_key = lambda x: tuple(key(x) for key in sort_keys)
        user_data = sorted(user_data, key=sort_key)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(user_data)

    # Select and reorder columns, ignoring missing columns
    df = df[[col for col in column_order if col in df.columns]]

    if len(df):
         # Dislay title of finding
        print(f"\n{'-'*10} {finding_title}: {len(df)} Results {'-'*10}\n")
        
        #print(df.to_csv(index=False))
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    
def find_duplicate_usernames_with_same_hash(user_data):
    # Track domains and password hashes for each username
    user_hash_domains = defaultdict(lambda: defaultdict(set))
    for entry in user_data:
        user_hash_domains[entry['user'].lower()][entry['password_hash']].add(entry['domain'])

    # Find usernames that appear in more than one domain with the same password hash
    valid_entries = []
    for user, hashes in user_hash_domains.items():
        for password_hash, domains in hashes.items():
            if len(domains) > 1:
                # Add valid entries to the list
                valid_entries.extend(
                    [entry for entry in user_data if entry['user'] == user and entry['password_hash'] == password_hash]
                )

    return valid_entries    

def find_similar_usernames_with_same_hash(user_data):
    # Find usernames that appear in more than one domain with the same password hash
    valid_entries = []
    for user1 in user_data:
        kinda_a_match = False
        for user2 in user_data:
            if user1['password_hash'] == user2['password_hash'] and user1['password_hash'] !="31d6cfe0d16ae931b73c59d7e0c089c0":
                if user1["user"].lower() != user2["user"].lower():
                    if user1["user"].lower() in user2["user"].lower() or user2["user"].lower() in user1["user"].lower():
                        kinda_a_match=True
                    else:
                        similarity_ratio = SequenceMatcher(None, user1["user"].lower(), user2["user"].lower()).ratio() 
                        if similarity_ratio > 0.59:
                            kinda_a_match=True
        if kinda_a_match:
            valid_entries.append(user1)

    return valid_entries 

def is_weak_password(password, domain):  
    domain_parts = domain.split(".")
    for part in domain_parts[:-1]:
        if len(part) >= 3:
            similarity_ratio = SequenceMatcher(None, password.lower(), part.lower()).ratio() 
            if similarity_ratio > 0.50:
                return "Password Close to Domain name"
    
    # Compile regex patterns
    season_year_pattern = re.compile(rf'sS]pring\d{{2}}|sS]ummer\d{{2}}|fF]all\d{{2}}|wW]inter\d{{2}}', re.IGNORECASE)
    mono_character_pass = re.compile(r'^\d+$|^\w+$', re.IGNORECASE)

    password_variation_pattern = re.compile(r'p[^\w]*a[^\w]*s[^\w]*s[^\w]*w[^\w]*o[^\w]*r[^\w]*d', re.IGNORECASE)
    min_length = 8
    character_type_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#;?&])', re.IGNORECASE)

    if len(password) < min_length:
        return "Password Less than 8 chars"
    if not character_type_pattern.search(password):
        return "Low password complexity"
    if season_year_pattern.search(password):
        return "Season/Password Combo"
    if mono_character_pass.fullmatch(password):
        return "All the same char type"

    if password_variation_pattern.search(password):
        return "Password Variance Issue"
    return False

def return_hash_collisions(user_data):
    grouped_users=[]
    for user in user_data:
        for other_user in user_data:
            if user != other_user and user["password_hash"] == other_user["password_hash"] and user not in grouped_users:
                grouped_users.append(user)
                
    return grouped_users
    
def display_only_current_users(user_data):
    current_accounts=[]
    for user in user_data:
        if "_history" not in user["user"]:
            current_accounts.append(user)
                
    return current_accounts    

def crack_them(hash_file, guess_file, rules_arg, rules_file, users_true, quiet_mode, hash_mode, self_test_disable):
    pattern = r'(\d+)/\d+\s+\((\d+\.\d+)%\) Digests \(new\)'
    match = ""
    base_hashcat_command = ["hashcat", "-O", "-w", "4", "-m", hash_mode]
    hashcat_command = base_hashcat_command + [hash_file, guess_file]

    if rules_arg:
        hashcat_command += ["--rules", rules_file]
    if users_true:
        hashcat_command.append("--user")
    if quiet_mode:
        hashcat_command.append("--quiet")
    if self_test_disable:
        hashcat_command += " --self-test-disable"
        
    crack_run = subprocess.Popen(hashcat_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
    new_cracks = 0
    
    #print(" ".join(hashcat_command))
    
    for line in crack_run.stdout:
        if "Failed" not in line and "[c]heckpoint" not in line:
            print(line, end='') 
            if quiet_mode:
                new_cracks += 1
            else:
                if "Digests" in line:
                    match = re.search(pattern, line)

    crack_run.wait()

    if not quiet_mode:
        if match:
            new_cracks = int(match.group(1))

    if crack_run.returncode == 1:
        return new_cracks
    elif crack_run.returncode != 0:
        raise Exception(f"Hashcat failed with return code: {crack_run.returncode}")
        exit()

def detect_mode(hash_file, users_true, empty_file):
    hashcat_command = f"hashcat {hash_file} {empty_file} --self-test-disable"
    if users_true:
        hashcat_command += " --user"

    get_mode_run = subprocess.Popen(hashcat_command.strip().split(" "), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
    options = []

    for line in get_mode_run.stdout:
        if "|" in line:
            option_parts = line.strip().split("|")
            options.append(option_parts)

    get_mode_run.wait()
    sys.stdin.flush()

    if len(options) == 0:
        print("\nThere were no hash matches. Do you need -u for usernames perhaps? \n\nCheck your hashes and specify a type.\n\nExiting...\n")
        sys.exit(1)

    print("### Possible Hashtype matches ###")
    for i, option in enumerate(options):
        print(f"{i+1}. {' | '.join(option)}")

    if len(options) == 1:
        selected_option = options[0]
        new_mode = selected_option[0].strip()
        print(f"\nThis was the only detected match: {new_mode}")
        return new_mode

    entered_option = input("Enter the index number or hash mode you want to select: ")

    while not entered_option.isdigit():
        entered_option = input("Invalid input. Enter the index number or hash mode you want to select: ")

    if int(entered_option) <= len(options):
        selected_index = int(entered_option) - 1
        selected_option = options[selected_index]
        new_mode = selected_option[0].strip()
    else:
        if entered_option not in [option[0].strip() for option in options]:
            confirm = input("\nThat wasn't provided, are you sure (YES/no): ")
            if confirm.lower() not in ["yes", "y", ""]:
                entered_option = input("\nTell me what it should be then: ")

        new_mode = entered_option.strip()

    return new_mode
         
def extract_results(hashcat_folder, hashcat_results_folder):

    if platform.system() == "Windows":
        pot_file = os.path.join(hashcat_folder, "hashcat.potfile")
    else:
        pot_file = os.path.join(hashcat_results_folder, "hashcat.potfile")
        
    output_file = os.path.join(hashcat_results_folder, "cracked_passwords.txt")

    # Read existing cracked passwords
    existing_passwords = set()
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            for line in f:
                existing_passwords.add(line.strip())
                

    # Read new cracked passwords from pot file
    with open(pot_file, "r") as f:
        lines = f.readlines()

    new_passwords = set()
    for line in lines:
        columns = line.strip().split(":")
        if len(columns) > 1:
            new_passwords.add(columns[1])

    # Combine existing and new cracked passwords
    combined_passwords = sorted(existing_passwords | new_passwords)

    # Write combined unique sorted passwords to file
    with open(output_file, "w") as f:
        for password in combined_passwords:
            f.write(f"{password}\n")

def do_the_thing():
    parser = argparse.ArgumentParser(description="Hashcat automation script.")

    parser.add_argument("-f", "--file", type=validate_file, required=True, help="Path to the dumped file.")
    parser.add_argument("-r", "--rules", type=validate_file, nargs='?', const=True, default=None, help="Allows you to run rules. defaults to OneRuleToRuleThemStill")
    parser.add_argument("-u", "--user", action='store_true', default=False, help="If your input has the user. then you need this")
    parser.add_argument("-s", "--show", action='store_true', default=False, help="Show cracked Results for file")
    parser.add_argument("-q", "--quiet", action='store_true', default=False, help="Experimental mode to only show the results and nothing else.")
    parser.add_argument("-w", "--wordlist", type=validate_file, default=None, help="to supply a wordlist that is not rockyou.txt")
    parser.add_argument("-d", "--disable", action='store_true', default=False, help="Disable self test if hashcat is being a pain.")
    parser.add_argument("-m", "--mode", help="Manually set hash type")
    parser.add_argument("-a", "--analysis", action='store_true', default=False, help="Findings Analysis for select hashtypes (NTLM)")

    args = parser.parse_args()

    hashcat_folder, hashcat_results_folder = prereq_setup()
    os.chdir(hashcat_folder)

    if not args.show:
        check_drivers(hashcat_folder)

    if not args.wordlist:
        guess_file = os.path.join(hashcat_results_folder, "rockyou.txt")
    else:
        guess_file = args.wordlist

    if not args.rules:
        rules_file = os.path.join(hashcat_results_folder, "OneRuleToRuleThemStill.rule")
    else:
        rules_file = args.rules    

    if not args.mode:
        
        empty_file= os.path.join(hashcat_results_folder, "empty.txt")
        final_mode = detect_mode(args.file, args.user, empty_file)
    else:
        final_mode = args.mode

    if not args.show:
        crack_them(args.file, guess_file, args.rules, rules_file, args.user, args.quiet, final_mode, args.disable)

        reattack = True
        while reattack:
            print("recursing...")

            extract_results(hashcat_folder, hashcat_results_folder)
            guess_file = os.path.join(hashcat_results_folder, "cracked_passwords.txt")

            #enable rules anbd set crack passwords.txt
            new_hashes_discovered = crack_them(args.file, guess_file, True, rules_file, args.user, args.quiet, final_mode, args.disable)
            if new_hashes_discovered == 0:
                reattack = False
                
        print("\n\n")
        
    show_command = f"hashcat -m {final_mode} {args.file} --show "
    if args.user:
        show_command += " --user"
        

    show_run = subprocess.Popen(show_command.strip().split(" "), stdout=subprocess.PIPE, universal_newlines=True)

    hashcat_results = []
    for line in show_run.stdout:
        hashcat_results.append(line.strip())

    if args.analysis:
        print()

        user_data = []
        parse_hash_file(args.file, user_data, final_mode)
        parse_hashcat(hashcat_folder, hashcat_results_folder, user_data, final_mode)

        if final_mode == "1000":
            current_users = display_only_current_users(user_data)
            collisions = return_hash_collisions(current_users)

            ############################
            #        Bad Passwords     #
            ############################
            finding_title = "Not the Best Passwords"
            column_order = ["user", "domain", "password", "user_status", "password_issue"]

            for user in user_data:
                user["password_issue"] = is_weak_password(user['password'], user['domain'])

            array_filter = lambda x: x['password'] != '' and is_weak_password(x['password'], x['domain'])
            sort_keys = [lambda x: x['password_issue'].lower()]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ######################################
            # Show Cracked Passwords For Enabled #
            ######################################
            finding_title = "Cracked Passwords for Enabled Users"
            column_order = ["user", "domain", "password", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password'] != '' and x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0" and x["user_status"] == "Enabled"
            sort_keys = [lambda x: x['user'].lower(), lambda x: x['password'].lower()]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ############################
            #   Show Cracked Passwords #
            ############################
            finding_title = "Cracked Passwords for all users"
            column_order = ["user", "domain", "password", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password'] != ""
            sort_keys = [lambda x: x['password'].lower(), lambda x: x['user'].lower(), lambda x: x['domain'].lower()]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ######################################
            # Show Cracked Passwords For Status Unknown #
            ######################################
            finding_title = "Cracked Passwords for Status Unknown Users"
            column_order = ["user", "domain", "password", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password'] != '' and x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0" and x["user_status"] == "Unknown"
            sort_keys = [lambda x: x['user'].lower()]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ######################################
            # Show Cracked Passwords For Disabled #
            ######################################
            finding_title = "Cracked Passwords for Disabled Users"
            column_order = ["user", "domain", "password", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password'] != '' and x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0" and x["user_status"] == "Disabled"
            sort_keys = [lambda x: x['user'].lower()]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ######################################
            # Stale Passwords for enabled users  #
            ######################################
            from datetime import datetime

            def age_in_days(date_str):
                if date_str:
                    input_date = datetime.strptime(date_str, '%Y-%m-%d')
                    current_date = datetime.now()
                    difference = current_date - input_date
                    return int(difference.days)
                else:
                    return 0

            finding_title = "Stale Passwords for enabled users ( age > 500 days)"
            column_order = ["user", "domain", "password", "password_hash", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['user_status'] == 'Enabled' and age_in_days(x['pwdLastSet']) >= 500
            sort_keys = [lambda x: x['pwdLastSet']]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ################################
            #  Cracked Hash Collision      #
            ################################
            finding_title = "Cracked Hash Collisions"
            column_order = ["user", "domain", "password", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password'] != ''
            sort_keys = [lambda x: x['password'], lambda x: x['user'].lower()]

            display_results(finding_title, collisions, column_order, array_filter, sort_keys, sort_by_freq='password_hash')

            ################################
            #  Enabled User w/ Hash Collision  #
            ################################
            finding_title = "Enabled User w/ Hash Collision"
            column_order = ["user", "domain", "password_hash", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['user_status'] == 'Enabled' and x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0"
            sort_keys = [lambda x: x['password_hash'], lambda x: x['user'].lower()]

            display_results(finding_title, collisions, column_order, array_filter, sort_keys, sort_by_freq='password_hash')

            ################################
            #  All Hash Collision  #
            ################################
            finding_title = "All Hash Collision"
            column_order = ["user", "domain", "password_hash", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0"
            sort_keys = [lambda x: x['password_hash'], lambda x: x['user'].lower()]

            display_results(finding_title, collisions, column_order, array_filter, sort_keys, sort_by_freq='password_hash')
            
            ############################
            # Same user/pass in different domain #
            ############################
            finding_title = "Same user/hash check in multiple domains"
            column_order = ["user", "domain", "password_hash", "password", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0"
            sort_keys = [lambda x: x['user'].lower(), lambda x: x['domain']]

            filtered_data = find_duplicate_usernames_with_same_hash(current_users)
            display_results(finding_title, filtered_data, column_order, array_filter, sort_keys, sort_by_freq='password_hash')

            ###################################
            # Similar user in different domain #
            ###################################
            finding_title = "Similar user/hash in different domain"
            column_order = ["user", "domain", "password_hash", "password", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0"
            sort_keys = [lambda x: x['password_hash'].lower(), lambda x: x['user'], lambda x: x['domain']]

            filtered_data = find_similar_usernames_with_same_hash(current_users)
            display_results(finding_title, filtered_data, column_order, array_filter, sort_keys, sort_by_freq='password_hash')

            ################################
            #  Unracked Hash Collision     #
            ################################
            finding_title = "Uncracked Hash Collisions"
            column_order = ["user", "domain", "password_hash", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password'] == '' and x['password_hash'] != "31d6cfe0d16ae931b73c59d7e0c089c0"
            sort_keys = [lambda x: x['password_hash'], lambda x: x['user'].lower()]

            display_results(finding_title, collisions, column_order, array_filter, sort_keys, sort_by_freq='password_hash')

            ############################
            #        Show LM_HASH      #
            ############################
            finding_title = "Users with LM Hashes"
            column_order = ["user", "domain", "lm_hash", "password_hash", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['lm_hash'] != "aad3b435b51404eeaad3b435b51404ee"
            sort_keys = [lambda x: x['lm_hash']]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ############################
            #   Show Blank Passwords   #
            ############################
            finding_title = "Blank Password Hash (Likely Disabled)"
            column_order = ["user", "domain", "password_hash", "user_status", "pwdLastSet"]
            array_filter = lambda x: x['password_hash'] == "31d6cfe0d16ae931b73c59d7e0c089c0"
            sort_keys = [lambda x: x['user'].lower()]

            display_results(finding_title, current_users, column_order, array_filter, sort_keys)

            ############################
            #   Cracked Historical Passwords   #
            ############################
            finding_title = "Cracked Historical Passwords"
            column_order = ["user", "domain", "password"]
            array_filter = lambda x: x['history_user'] != False and x['password'] != ""
            sort_keys = [lambda x: x['user'].lower(), lambda x: int(x['history_user'])]

            display_results(finding_title, user_data, column_order, array_filter, sort_keys)

            
            ################################
            # Cracked Historical Passwords #
            ################################
            
            # Calculate statistics
            cracked = sum(1 for user in user_data if user["password"])
            current_cracked = sum(1 for user in user_data if user["password"] and not user["history_user"])

            total_hashes = len(user_data)
            current_users = sum(1 for user in user_data if not user["history_user"])
            historical_hashes_cracked = cracked - current_cracked
            percentage_current_cracked = 100 * (current_cracked / current_users) if current_users else 0
            percentage_historical_cracked = 100 * (cracked / total_hashes) if total_hashes else 0

            # Prepare statistics table data
            stats_data = [
                ["Total number of hashes", total_hashes],
                ["Number of current users", current_users],
                ["Number of hashes cracked", cracked],
                ["Number of current users cracked", current_cracked],
                ["Percentage of current users cracked", f"{percentage_current_cracked:.2f}%"],
                ["Number of historical passwords cracked", historical_hashes_cracked],
                ["Percentage of historical passwords cracked", f"{percentage_historical_cracked:.2f}%"]
            ]

            # Print statistics table
            print("\nStatistics:\n")
            print(tabulate(stats_data, headers=["Metric", "Value"], tablefmt='grid'))


        else:
            print(f"\nAnalysis not available for this hashtype: {final_mode}\n")
            for line in sorted(hashcat_results):
                if "31d6cfe0d16ae931b73c59d7e0c089c0:" not in line and "aad3b435b51404eeaad3b435b51404ee:" not in line and "Failed to parse" not in line:
                    print(line)
                    
                    


    else:
        for line in sorted(hashcat_results):
            if "31d6cfe0d16ae931b73c59d7e0c089c0:" not in line and "aad3b435b51404eeaad3b435b51404ee:" not in line and "Failed to parse" not in line:
                print(line)

    show_run.wait()

if __name__ == "__main__":
    do_the_thing()
	
