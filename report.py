import json
from colorama import Fore, Style, init

init(autoreset=True)

def print_report(file_path, findings, json_mode=False):
    if json_mode:
        print(json.dumps({
            "file": file_path,
            "suspicious_findings": findings
        }, indent=2))
    else:
        print(f"{Style.BRIGHT}📄 Analyzing: {file_path}")
        if not findings:
            print(f"{Fore.GREEN}✅ No suspicious patterns found.")
        else:
            print(f"{Fore.RED}⚠️ Suspicious patterns found:")
            for f in findings:
                print(f"{Fore.YELLOW} - {f}")
