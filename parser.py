import re

def parse_nsi_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments
    content = re.sub(r';.*', '', content)

    # Tokenize commands
    commands = re.findall(r'(?i)^\s*(\w+)[ \t]*(.*)', content, flags=re.MULTILINE)

    parsed = [{"command": cmd.lower(), "args": args.strip()} for cmd, args in commands]
    return parsed
