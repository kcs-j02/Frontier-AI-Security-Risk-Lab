# 生成AIを補助的に用いたSSH設定リスク分析

> フロンティアAIを参考にした生成AIリスク分析の中心記録。実際のCRX製品を利用した結果ではありません。

## 取得した設定

Ubuntuの `sudo sshd -T` から以下を確認しました。

```text
port 22
permitrootlogin prohibit-password
pubkeyauthentication yes
passwordauthentication yes
```

## 仮説と評価

`passwordauthentication yes` により、SSHへ到達できる接続元はパスワード認証を試行できます。一般にパスワード推測や資格情報の悪用の機会となり得るため、必要性を検討する対象です。**この設定自体を脆弱性と断定していません**。

また `permitrootlogin prohibit-password` はrootのパスワード認証ログインを禁止しますが、鍵を使ったrootログインの可能性は残します。`port 22` は標準ポートの利用であって、それ自体が脆弱性ではありません。

当初の接続検証では、Kali側 `192.168.2.100` からUbuntu側 `192.168.1.101:22` への接続が成立し、パスワード認証でログインしました。これは「KaliからのSSH接続が不要なら接続元を制限すべき」という**実験上のリスク仮説**を裏付けます。実際の企業環境における必要性は業務要件に左右されます。

## 対策

1. **ネットワーク**: pfSense OPT1のPassルールを無効化し、KaliからUbuntuへの新規SSH通信を遮断。
2. **認証**: WindowsのED25519公開鍵をUbuntu `authorized_keys` に登録し、認証成功を確認してから `PasswordAuthentication no` に変更。`KbdInteractiveAuthentication no` も確認。
3. **実証**: 接続結果とpfSense/Ubuntu双方のログを比較。

生成AIは論点整理の補助です。独立した自動診断ツールを構築したわけではありません。最終的な判断は設定値と実測に基づきます。

![SSH initial state](../images/07-ssh-settings-before.png)
