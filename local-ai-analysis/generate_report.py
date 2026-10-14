from pathlib import Path

from datetime import datetime



base = Path.home() / "security-ai"



files = {

    "SSH Configuration": "ssh_config.txt",

    "Network and Firewall": "network_config.txt",

    "AI Analysis": "security_analysis.txt",

    "Verification Results": "verification.txt",

    "AI Evaluation": "evaluation.txt",

    "Post-verification AI Analysis": "verification_analysis.txt",

}



report = [

    "# AI Security Risk Analysis Report",

    "",

    f"Generated: {datetime.now().isoformat(timespec='seconds')}",

    "",

    "## Purpose",

    "Evaluate AI-generated security findings against "

    "SSH settings, firewall rules, and observed connection tests.",

    "",

]



for title, filename in files.items():

    path = base / filename

    report.append(f"## {title}")

    report.append("")

    if path.exists():

        report.append("```text")

        report.append(path.read_text(encoding="utf-8"))

        report.append("```")

    else:
        report.append(f"Missing file: {filename}")



output = base / "auto_report.md"

output.write_text("\n".join(report), encoding="utf-8")



print(f"Report saved: {output}")
