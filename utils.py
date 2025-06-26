SUSPICIOUS_COMMANDS = {
    'WriteRegStr': 2,
    'DeleteRegKey': 3,
    'Exec': 2,
    'ExecWait': 2,
    'DownloadFile': 5,
    'ShellExec': 3,
    'Delete': 2,
    'CopyFiles': 1,
    'Rename': 1,
    'CreateShortCut': 1,
}

SUSPICIOUS_KEYWORDS = {
    'powershell': 4,
    'cmd.exe': 3,
    'startup': 3,
    'runonce': 4,
    'wget': 3,
    'curl': 3,
    'vbs': 3,
    'invoke-webrequest': 5,
    'certutil': 5,
    'bitsadmin': 5,
    'mshta': 5,
    'reg add': 4,
    'reg delete': 4,
    'base64': 3,
    'encodedcommand': 5,
    'taskkill': 3,
    'schtasks': 4,
    'net user': 3,
}

def calculate_suspicion_score(commands, lines):
    score = 0

    # Score commands
    for cmd in commands:
        score += SUSPICIOUS_COMMANDS.get(cmd, 0)

    # Score keywords (case insensitive)
    lower_lines = [line.lower() for line in lines]
    for keyword, weight in SUSPICIOUS_KEYWORDS.items():
        if any(keyword in line for line in lower_lines):
            score += weight

    return score
