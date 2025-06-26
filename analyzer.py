from utils import calculate_suspicion_score, SUSPICIOUS_COMMANDS, SUSPICIOUS_KEYWORDS

def analyze(nsi_path):
    with open(nsi_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Extract commands
    commands = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(';'):
            continue
        parts = stripped.split()
        if parts:
            cmd = parts[0]
            commands.append(cmd)

    # Calculate score
    score = calculate_suspicion_score(commands, lines)

    # Detect suspicious elements
    found_cmds = [cmd for cmd in commands if cmd in SUSPICIOUS_COMMANDS]
    found_keywords = []
    lower_lines = [line.lower() for line in lines]
    for keyword in SUSPICIOUS_KEYWORDS:
        if any(keyword in line for line in lower_lines):
            found_keywords.append(keyword)

    # Prepare findings
    findings = []
    if found_cmds:
        findings.append(f"Suspicious commands detected: {', '.join(sorted(set(found_cmds)))}")
    if found_keywords:
        findings.append(f"Suspicious keywords detected: {', '.join(sorted(set(found_keywords)))}")
    findings.append(f"Suspicion score: {score:.2f}")

    # Add final flag
    threshold = 7
    if score >= threshold:
        findings.append("⚠️ Installer flagged as suspicious!")
    else:
        findings.append("✅ Installer appears clean.")

    return score, findings
