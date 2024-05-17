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
            print(f"Error: {e}")
            return None
    else:
        print("This script only supports Windows.")
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
            print(f"Error: {e}")
            return None
    else:
        print("This script only supports Windows.")
        return None

def check_AMD_drivers():
    verify_install="driverquery /v /nh"

    AMD_driver_found=False
    #try:
    x=subprocess.run(verify_install,stdout=subprocess.PIPE, universal_newlines=True)
    lines=x.stdout.split('\n')
    for line in lines:
        if "Adrenalin" in line:
            AMD_driver_found=True
            print("AMD Drivers installed")
                
    if AMD_driver_found:
        print("AMD Drivers installed")
    else:
        print("AMD Drivers not installed")
        url = "https://www.amd.com/en/support"
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')

        download_link = None

        for a in soup.find_all('a'):
            if a.text == "Download Now":
                download_link = a['href']
                break
        
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',  "Referer": "https://www.amd.com/"}
        response = requests.get(download_link, headers=headers, verify=False)
        
        exe_name = "amd_installer.exe"
        
        with open(exe_name, "wb") as exe_file:
            exe_file.write(response.content)

        print(f"{exe_name} downloaded. Starting installation...")
        os.system(f"start {exe_name}")
        
        
        AMD_driver_found=False
        x=subprocess.run(verify_install,stdout=subprocess.PIPE, universal_newlines=True)
        lines=x.stdout.split('\n')
        for line in lines:
            if "Adrenalin" in line:
                AMD_driver_found=True
                print("AMD Drivers installed")
        
        if AMD_driver_found:
            print("AMD Drivers installed")
        else:
            print("AMD Driver install failed. Exiting")
            exit()

def check_Cuda_drivers():
    verify_install="nvcc --version"

    try:
        subprocess.run(verify_install,stdout=subprocess.PIPE)
    except:
        print("Cuda Drivers not installed. Please install latest version")
        os.system("start https://developer.nvidia.com/cuda-downloads")
        exit()      
    
def check_NVIDIA_drivers():
    verify_install="nvidia-smi --query-gpu=driver_version --format=csv,noheader"
    try:
        driver_version = subprocess.check_output(verify_install.split(" "))

        # Convert driver version to float
        driver_version = float(driver_version)

        # Check if driver version is greater than 440.64
        if driver_version > 440.64:
            return
    except:
        pass
        
    verify_install='''wmic path win32_VideoController get Name'''
    
    wmic_output=subprocess.run(verify_install,stdout=subprocess.PIPE, universal_newlines=True)
    device_names=wmic_output.stdout.split('\n')
    for device in device_names:
        if "NVIDIA" in device:
            print(f"Issue finding appropriate NVIDIA Driver. Download correct version (>440) for \"{device.strip()}\"")
            os.system("start https://www.nvidia.com/Download/index.aspx")
    exit()
   
def check_Intel_OpenCL_drivers():
    verify_install=".\hashcat.exe -I"
    try:
        output = subprocess.check_output(verify_install.split(" ")).decode('utf-8')
        # Search the output for "intel.*OpenCl" using a regular expression
        pattern = re.compile(r'Intel.*OpenCL')
        match = pattern.search(output)

        # Check if the pattern was found in the output
        if match:
            return
    except:
        print("Intel OpenCL not detected by hashcat. Please install latest version of OpenCL Runtime for Intel Core and Intel Xeon Processors")
        os.system("https://www.intel.com/content/www/us/en/developer/tools/opencl-cpu-runtime/overview.html")
        exit()      

def check_drivers():
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
        check_Intel_OpenCL_drivers()

def prereq_setup():

    url = 'https://hashcat.net/hashcat/'
    response = requests.get(url, verify=False)
    content = response.content

    soup = BeautifulSoup(content, 'html.parser')
    version_div = soup.select_one('#download table tr td a')['href']

    # Join the relative path with the base url to get the full URL
    file_url = urljoin(url, version_div)

    # Extract the version number from the URL
    version = re.search(r'hashcat-(\d+\.\d+\.\d+)', file_url).group(1)

    # Set the desired location for Hashcat
    see_hashcat_folder = "C:\\hashcat"

    # Create the see_hashcat_folder folder if it doesn't exist
    os.makedirs(see_hashcat_folder, exist_ok=True)

    # Set the path to your 7-Zip executable (change it if necessary)
    seven_zip_executable = "C:\\Program Files\\7-Zip\\7z.exe"

    hashcat_folder = os.path.join(see_hashcat_folder, f"hashcat-{version}")
    
    empty_file= os.path.join(see_hashcat_folder, "empty.txt")
    
    with open(empty_file, 'w') as file:
        pass 

    if not os.path.exists(hashcat_folder):
        print(f"Current Hashcat version: {version}")

        # Download the file at the full URL
        urlretrieve(file_url, "hashcat.7z")

        print("Downloaded hashcat.7z")

        # Run the 7-Zip command-line executable to extract the archive directly into the see_hashcat_folder folder
        subprocess.run([seven_zip_executable, "x", "-y", "-o" + see_hashcat_folder, "hashcat.7z"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"Unzipped hashcat.7z to {see_hashcat_folder}")

        # Optionally, delete the original downloaded 7z file
        os.remove("hashcat.7z")

        print("Cleaned up downloaded file")

        # Change the working directory to the hashcat folder
        os.chdir(hashcat_folder)

        # Run hashcat.exe with the -b option
        test_run = subprocess.run(["hashcat.exe", "-b", "-m", "1000", "-O", "-D", "1,2,3", "-w", "4"])
        if test_run.returncode != 0:
            raise Exception(f"Hashcat benchmark failed with return code: {result.returncode}")
            exit()
    else:
        #print(f"Hashcat {version} is current.")
        hashcat_folder = os.path.join(see_hashcat_folder, f"hashcat-{version}")
        os.chdir(hashcat_folder)

    rockyou_file = os.path.join(hashcat_folder, "rockyou.txt")

    if not os.path.exists(rockyou_file):
        urlretrieve('https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt', rockyou_file)
        print(f"Downloaded rockyou.txt")

    one_rule_file = os.path.join(hashcat_folder, "OneRuleToRuleThemStill.rule")

    if not os.path.exists(one_rule_file):
        urlretrieve('https://raw.githubusercontent.com/stealthsploit/OneRuleToRuleThemStill/main/OneRuleToRuleThemStill.rule', one_rule_file)
        print(f"Downloaded OneRuleToRuleThemStill.rule")
    
    
    return hashcat_folder
    
def validate_file(f):
    if not os.path.exists(f):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return os.path.abspath(f).replace('\\', '/')

def crack_them(hash_file,guess_file,rules_file,users_true,quiet_mode,hash_mode,self_test_disable):
    # define the pattern to match the new digest percentages
    pattern = r'(\d+)/\d+\s+\((\d+\.\d+)%\) Digests \(new\)'
    match = ""

    # create command
    base_hashcat_command = ["hashcat.exe", "-O", "-w", "4"]
    
    # Append the file paths and additional options directly to the command list
    hashcat_command = base_hashcat_command + [hash_file, guess_file]
    
    if rules_file:
        if rules_file == True:
            rules_file = "OneRuleToRuleThemStill.rule"
        hashcat_command += ["--rules", rules_file]
    if users_true:
        hashcat_command.append("--user")
    if quiet_mode:
        hashcat_command.append("--quiet")
    if self_test_disable:
        hashcat_command += " --self-test-disable"    

    
    # Print the command for debugging
    print("Running:", ' '.join(hashcat_command))
    
    # Run hashcat.exe against the file
    crack_run = subprocess.Popen(hashcat_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
    
    new_cracks=0
   
    for line in crack_run.stdout:
        if "Failed" not in line and "[c]heckpoint" not in line:
            print(line, end='') # show live output
            if quiet_mode:
                new_cracks+=1
            else:
                if "Digests" in line:
                    match = re.search(pattern,line)

    # wait for the subprocess to complete
    crack_run.wait()
    
    if not quiet_mode:
        if match:
              # extract the matched percentage value as a float
            new_cracks = int(match.group(1))
    
    #Recovered........: 15/186 (8.06%) Digests (total), 1/186 (0.54%) Digests (new) 
    
    if crack_run.returncode == 1:
        #print("Hashcat cracked all it could with this level")
        return new_cracks
    elif crack_run.returncode != 0:
        raise Exception(f"Hashcat failed with return code: {crack_run.returncode}")
        exit()   

def detect_mode(hash_file,users_true):
    #empty file to stop it being input mode
    hashcat_command=f"hashcat.exe {hash_file} C:\hashcat\empty.txt --self-test-disable"
    #hashcat_command=f"hashcat.exe {hash_file}"

    if users_true:
        hashcat_command += " --user"
        
    # Run hashcat.exe agaisnt file
    get_mode_run = subprocess.Popen(hashcat_command.strip().split(" "), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    universal_newlines=True)
    
    options = []  # create an empty list to store the options
    for line in get_mode_run.stdout:
        #print(line, end="")
        if "|" in line:
            option_parts = line.strip().split("|")
            options.append(option_parts)  # append the full option to the list
        
    get_mode_run.wait()
    sys.stdin.flush()

    if len(options) == 0:
        print("\nThere were no hash matches. Do you need -u for usernames perhaps? \n\nCheck your hashes and specify a type.\n\nExiting...\n")
        sys.exit(1)
    
    
    # print the options
    print("### Possible Hashtype matches ###")
    for i, option in enumerate(options):
        print(f"{i+1}. {' | '.join(option)}")
    

    #if there is only one option use it    
    if len(options) == 1:
        selected_option=options[0]
        new_mode=selected_option[0].strip()
        print(f"\nThis was the only detected match: {new_mode}")
        return new_mode 
        
    # ask the user for input
    entered_option = input("Enter the index number or hash mode you want to select: ")

    # validate the input
    while not entered_option.isdigit():
        entered_option = input("Invalid input. Enter the index number or hash mode you want to select: ")
    
    if int(entered_option) <= len(options):
        selected_index = int(entered_option) - 1
        selected_option = options[selected_index]
        new_mode=selected_option[0].strip()
    else:
        if entered_option not in [option[0].strip() for option in options]:
            confirm = input("\nThat wasn't provided, are you sure (YES/no): ")
            if confirm.lower() not in ["yes", "y", ""]:
                entered_option = input("\nTell me what it should be then: ")

        new_mode=entered_option.strip()
        
    return new_mode
         
def extract_results():
    pot_file = "hashcat.potfile"
    output_file = "cracked_passwords.txt"

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
    # Argument parsing
    parser = argparse.ArgumentParser(description="Hashcat automation script.")

    #File passed in
    parser.add_argument("-f", "--file", type=validate_file, required=True, help="Path to the dumped file.")

    #command components
    parser.add_argument("-r", "--rules", type=validate_file, nargs='?', const=True, default=None, help="Allows you to run rules. defaults to OneRuleToRuleThemStill")
    parser.add_argument("-u", "--user", action='store_true', default=False, help="If your input has the user. then you need this")
    parser.add_argument("-s", "--show", action='store_true', default=False, help="Show cracked Results for file")
    parser.add_argument("-q", "--quiet", action='store_true', default=False, help="Experimental mode to only show the results and nothing else.")
    parser.add_argument("-w", "--wordlist", type=validate_file, default=None, help="to supply a wordlist that is not rockyou.txt")
    parser.add_argument("-d", "--disable", action='store_true', default=False, help="Disable self test if hashcat is being a pain.")

    #mode or auto mode. default is 1000
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument("-m", "--mode", default="1000", help="Set custom mode. Default is 1000 for NTLM")
    exclusive_group.add_argument("-a", "--auto-mode",  action='store_true', default=False, help="Let it try to figure out the hash mode.")

    args = parser.parse_args()

    #setup
    prereq_setup()

    #check that all runtime drivers are 
    check_drivers()

    if not args.wordlist:
        guess_file="rockyou.txt"
    else:
        guess_file=args.wordlist

    if not args.show:
    
        #decide which mode to use
        if args.auto_mode:
            final_mode=detect_mode(args.file,args.user)
        else:
            final_mode=args.mode
        
        crack_them(args.file,guess_file,args.rules,args.user,args.quiet,final_mode,args.disable)

        reattack=True
        while reattack:
            print("recursing...")

            extract_results()
            guess_file="cracked_passwords.txt"

            new_hashes_discovered = crack_them(args.file,guess_file,True,args.user,args.quiet,final_mode,args.disable)
            print("new_hashes_discovered",new_hashes_discovered)
            if new_hashes_discovered == 0:
                reattack=False


    show_command=f"{os.getcwd()}\\hashcat.exe -m {final_mode} {args.file} --show "
    if args.user:
        show_command += " --user"

    print(f"Running: {show_command}")

    show_run = subprocess.Popen(show_command.strip().split(" "), stdout=subprocess.PIPE,
    universal_newlines=True)

    for line in show_run.stdout:
        if "Failed" not in line:
            print(line, end='') # show live output
      
    # wait for the subprocess to complete
    show_run.wait()

if __name__ == "__main__":
    do_the_thing()
