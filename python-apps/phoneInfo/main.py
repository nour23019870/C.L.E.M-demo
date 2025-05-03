import phonenumbers
from phonenumbers import carrier, geocoder, timezone, number_type, PhoneNumberFormat
import csv
import os
import requests
import sys
import time
import colorama
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init(autoreset=True)

IPQS_API_KEY = "YOUR_API_KEY_HERE"

def print_banner():
    os.system("clear" if os.name == "posix" else "cls")
    banner = f'''{Fore.CYAN}
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░      
░▒▓█▓▒░   ░▒▓████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░▒▓████████▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓████████▓▒░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
{Style.RESET_ALL}{Fore.GREEN}
                    ☎️  PH0N3 1NT3L TR4CK3R v1.0  ☎️                    
                    [+] Advanced Intelligence Tool [+]
{Style.RESET_ALL}'''
    print(banner)
    print(f"{Fore.YELLOW}{'=' * 70}{Style.RESET_ALL}")

def animate_text(text):
    for char in text:
        sys.stdout.write(f"{Fore.GREEN}{char}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.01)
    sys.stdout.write("\n")

def animate_progress(task):
    sys.stdout.write(f"{Fore.YELLOW}[*] {task}... {Style.RESET_ALL}")
    sys.stdout.flush()
    chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
    for _ in range(20):
        for char in chars:
            sys.stdout.write(f"\r{Fore.YELLOW}[*] {task}... {Fore.CYAN}{char}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.05)
    sys.stdout.write(f"\r{Fore.GREEN}[+] {task}... Complete!{' ' * 10}\n{Style.RESET_ALL}")

def ipqs_lookup(phone_number):
    animate_progress(f"Connecting to IPQS API for {phone_number}")
    url = f"https://www.ipqualityscore.com/api/json/phone/{IPQS_API_KEY}/{phone_number}"
    try:
        response = requests.get(url)
        data = response.json()

        if not data.get("success"):
            print(f"{Fore.RED}❗ IPQS error: {data.get('message', 'Unknown error')}{Style.RESET_ALL}")
            return {}

        return {
            "Fraud Score": data.get("fraud_score"),
            "Risk Level": data.get("risk_level"),
            "Is Spammer": data.get("is_spammer"),
            "Is Safe": data.get("is_safe"),
            "Phone Type": data.get("phone_type"),
            "Carrier": data.get("carrier"),
            "Line Type": data.get("line_type"),
            "Location": data.get("location"),
            "Country": data.get("country"),
            "Region": data.get("region"),
            "City": data.get("city"),
            "Latitude": data.get("latitude"),
            "Longitude": data.get("longitude"),
            "Timezone": data.get("timezone"),
            "Area Code": data.get("area_code"),
            "DID": data.get("did"),
            "Mobile": data.get("mobile"),
            "VoIP": data.get("voip"),
            "SMS Capable": data.get("sms_capable"),
            "MMS Capable": data.get("mms_capable"),
            "Current Carrier": data.get("current_carrier"),
            "Original Carrier": data.get("original_carrier"),
            "Leaked": data.get("leaked"),
            "Ported": data.get("ported"),
            "Active": data.get("active"),
            "Valid": data.get("valid"),
            "Possible": data.get("possible"),
            "Last Carrier Change": data.get("last_carrier_change"),
            "First Carrier Change": data.get("first_carrier_change"),
            "Total Carrier Changes": data.get("total_carrier_changes"),
            "Last Data Change": data.get("last_data_change"),
            "First Data Change": data.get("first_data_change"),
            "Total Data Changes": data.get("total_data_changes"),
        }

    except Exception as e:
        print(f"{Fore.RED}❗ Error contacting IPQS: {e}{Style.RESET_ALL}")
        return {}

def get_number_info(mobileNo_str):
    animate_progress("Parsing phone number")
    
    try:
        mobileNo = phonenumbers.parse(mobileNo_str)
        animate_progress("Extracting metadata")
        
        info = {
            "Input": mobileNo_str,
            "Formatted": phonenumbers.format_number(mobileNo, PhoneNumberFormat.E164),
            "Time Zones": timezone.time_zones_for_number(mobileNo),
            "Carrier": carrier.name_for_number(mobileNo, "en"),
            "Region": geocoder.description_for_number(mobileNo, "en"),
            "Country Code": mobileNo.country_code,
            "Number Type": number_type(mobileNo),
            "Valid (Local)": phonenumbers.is_valid_number(mobileNo),
            "Possible": phonenumbers.is_possible_number(mobileNo)
        }

        # Add IPQS data
        ipqs_data = ipqs_lookup(mobileNo_str)
        info.update(ipqs_data)

        print(f"\n{Fore.CYAN}📞 Phone Number Intelligence Report:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'=' * 70}{Style.RESET_ALL}")
        for key, value in info.items():
            # Color coding based on content
            if key.lower().startswith(("valid", "active", "possible")) and str(value).lower() == "true":
                value_str = f"{Fore.GREEN}{value}{Style.RESET_ALL}"
            elif key.lower().startswith(("fraud", "risky", "spammer", "leaked")) and str(value).lower() == "true":
                value_str = f"{Fore.RED}{value}{Style.RESET_ALL}"
            else:
                value_str = f"{Fore.WHITE}{value}{Style.RESET_ALL}"
                
            print(f"{Fore.CYAN}{key}: {value_str}")
        print(f"{Fore.YELLOW}{'=' * 70}{Style.RESET_ALL}")

        return info

    except phonenumbers.NumberParseException as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❗ Unexpected error: {e}{Style.RESET_ALL}")
    return None

def save_to_csv(info, filename="phone_log.csv"):
    animate_progress("Saving intelligence data")
    
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=info.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(info)
        print(f"{Fore.GREEN}[+] Intel saved to {filename}{Style.RESET_ALL}")

if __name__ == "__main__":
    print_banner()
    animate_text("Initializing phone reconnaissance system...")
    
    while True:
        print(f"\n{Fore.YELLOW}[?] {Style.RESET_ALL}", end="")
        number = input(f"Enter target phone number in international format (or type '{Fore.RED}exit{Style.RESET_ALL}'): ").strip()
        if number.lower() == 'exit':
            animate_text("Shutting down systems... Goodbye!")
            break
            
        info = get_number_info(number)
        if info:
            print(f"\n{Fore.YELLOW}[?] {Style.RESET_ALL}", end="")
            save = input(f"Save intelligence to database? (y/n): ").strip().lower()
            if save == 'y':
                save_to_csv(info)
