#!/usr/bin/env python3
"""Run controlled, repeatable Ollama security-analysis comparisons.

No external Python libraries required. The program does not score model outputs.
"""
import argparse
import datetime
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

CASES = [
    {
        "id": "ssh-settings",
        "evidence": (
            "Ubuntu Server の sshd -T 出力（対策前）:\n"
            "port 22\npermitrootlogin prohibit-password\n"
            "pubkeyauthentication yes\npasswordauthentication yes\n"
            "この資料にはネットワークの接続試験や認証ログは含まれない。"
        ),
        "question": "この設定から確実に言えること、言えないこと、対策、検証手順を説明してください。",
    },
    {
        "id": "same-lan-routing",
        "evidence": (
            "VMwareの構成：Windows 11=192.168.1.102/24（VMnet2）、"
            "Ubuntu Server=192.168.1.101/24（VMnet2）。"
            "pfSense LAN=192.168.1.1、OPT1=192.168.2.1。"
            "Kali=192.168.2.100/24（VMnet3）。"
            "KaliからUbuntuへのSSHはpfSense経由で制御する。"
            "WindowsとUbuntuの両方は同じVMnet2上にある。"
        ),
        "question": "WindowsからUbuntuへの通常のSSH通信がpfSenseを経由するか、Kaliとの違い、確認方法を述べてください。",
    },
    {
        "id": "idor-basket",
        "evidence": (
            "OWASP Juice Shop v20.3.0の検証。"
            "アカウントAの買い物カゴID=6、アカウントBのID=7。"
            "Aで認証中にGET /rest/basket/7を送るとHTTP 200でBの買い物カゴ情報を取得できた。"
            "routes/basket.tsの対象処理では、URLパラメータのIDでBasketModel.findOneを実行し、"
            "要求ユーザーがそのカゴの所有者か確認していなかった。"
            "サーバー側に認可チェックを追加した修正版ではA→BがHTTP 403、"
            "A→AとB→BはHTTP 200だった。"
        ),
        "question": "脆弱性の種類・原因・根本対策・修正後の検証範囲・残る未検証事項を整理してください。",
    },
]

SYSTEM = (
    "あなたは独立したセキュリティ評価者です。提供された事実にのみ基づき回答してください。"
    "観測済みの事実、推論、未検証事項を明確に区別してください。"
    "判断理由、具体的な対策、追加検証項目を述べてください。"
    "設定だけを根拠に攻撃成功を断定しないでください。"
)


def call_ollama(url, model, prompt, timeout, seed):
    data = json.dumps({
        "model": model,
        "system": SYSTEM,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "seed": seed},
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url.rstrip("/") + "/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.load(resp)
    return result.get("response", ""), result.get("done", False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["gemma3:4b", "qwen3:4b"])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", default="results.jsonl")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be >= 1")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    total = len(args.models) * len(CASES) * args.repeats
    n = 0
    for case in CASES:
        prompt = f"【証拠情報】\n{case['evidence']}\n\n【質問】\n{case['question']}"
        for repeat in range(1, args.repeats + 1):
            for model in args.models:
                n += 1
                started = time.monotonic()
                record = {
                    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "case": case["id"], "repeat": repeat, "model": model,
                    "seed": 42 + repeat, "temperature": 0,
                    "system": SYSTEM, "prompt": prompt,
                    "response": None, "success": False, "error": None,
                }
                try:
                    response, done = call_ollama(args.url, model, prompt, args.timeout, 42 + repeat)
                    record["response"] = response
                    record["success"] = bool(done and response.strip())
                    if not record["success"]:
                        record["error"] = "empty or incomplete response"
                except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
                    record["error"] = f"{type(exc).__name__}: {exc}"
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
                with output.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                status = "OK" if record["success"] else f"ERROR: {record['error']}"
                print(f"[{n}/{total}] {case['id']} / {model} / {repeat}: {status}", flush=True)
    print(f"Saved {total} trial records to {output}")
    print("These are model outputs, not scored accuracy results.")


if __name__ == "__main__":
    main()
