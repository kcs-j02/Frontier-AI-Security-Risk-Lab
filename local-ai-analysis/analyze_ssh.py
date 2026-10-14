import json

import urllib.request

from pathlib import Path


# SSH設定を読み込む
ssh_config = Path("ssh_config.txt").read_text(encoding="utf-8")
network_config = Path("network_config.txt").read_text(encoding="utf-8")
verification = Path("verification.txt").read_text(encoding="utf-8")

# AIへの分析指示
prompt = f"""
You are a cybersecurity analyst.

Analyze the following SSH server configuration.

{ssh_config}
NETWORK AND FIREWALL CONFIGURATION:

{network_config}
VERIFICATION RESULTS:

{verification}
Analyze the firewall rule carefully.



Important:

- Action: Pass defines what an enabled rule does.

- Disabled: Yes means this rule is inactive.

- Other firewall rules are unknown.

- Windows and Ubuntu are on the same subnet.



Answer these questions:

1. Is the Kali SSH pass rule active?

2. Can Kali access Ubuntu based on the available evidence?

3. Does Windows SSH traffic normally pass through pfSense?

4. What additional evidence is needed?



Do not assume that a disabled rule allows traffic.

Answer briefly in Japanese.

"""

# Ollama APIに送信
payload = {
    "model": "gemma3:4b",
    "prompt": prompt,
    "stream": False,
    "think": False,
    "options": {"num_predict": 300}
}

request = urllib.request.Request(
    "http://127.0.0.1:11434/api/generate",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(request, timeout=300) as response:
    result = json.load(response)

# 分析結果を保存
output = Path("verification_analysis.txt")
output.write_text(result["response"], encoding="utf-8")

print("Analysis completed.")
print(f"Saved to: {output.resolve()}")
