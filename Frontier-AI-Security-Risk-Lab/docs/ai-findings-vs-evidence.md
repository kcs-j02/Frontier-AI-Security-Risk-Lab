# 生成AIによるSSHリスク分析と実測結果の照合

## 位置付け

CRXソリューションの「フロンティアAI」に関心を持ち、**汎用生成AIによるリスク仮説の整理と、人手による検証・対策**を小規模に疑似体験した記録です。CRX製品やフロンティアAIの実装・機能を利用・再現したものではありません。

## 入力した実機データ

Ubuntu ServerのSSH有効設定（`sudo sshd -T`）：

```text
port 22
permitrootlogin prohibit-password
pubkeyauthentication yes
passwordauthentication yes
```

観測した通信環境：Kali `192.168.2.100`（VMnet3/OPT1）、Ubuntu `192.168.1.101`（VMnet2/LAN）、管理用Windows `192.168.1.102`（VMnet2/LAN）。

## AI分析内容と事実の対照

| 分析で取り上げたリスク仮説・対策候補 | 検証方法 | 実測結果 | 解釈 |
|---|---|---|---|
| パスワード認証が有効なSSHは、到達可能な送信元からパスワード認証を試され得る | `sshd -T`、ログイン試験、Ubuntu認証ログ | `PasswordAuthentication yes`、`Accepted password` を確認 | 有効設定と実際の認証を確認。ただし設定単独を脆弱性とは断定しない |
| SSHの接続元は管理業務に必要な範囲へ制限するべき | pfSenseのOPT1 Passルール有効時、KaliからSSH接続 | KaliからUbuntuへのログイン成功 | ラボにおける不要なアクセス経路を確認 |
| Kali側のSSH許可を外すと不要な新規接続を遮断できる | Passルール無効化後に再接続しFirewallログを確認 | 接続タイムアウト、該当通信のDefault denyログ | 通信制御に成功したと判断できる |
| 防御後も正規の管理アクセスを維持するべき | WindowsからUbuntuへSSHログイン | 管理接続成功 | WindowsとUbuntuは同じLANであり、pfSense転送ルールでWindowsを選択許可した証拠ではない |
| パスワード認証に依存しない認証方式を検討する | ED25519鍵を登録し、パスワード無効化後に認証方式別接続を試す | 公開鍵ログイン成功、パスワード専用試行拒否、`Accepted publickey` | Ubuntu側の認証強化を確認 |

## 再実験用の生成AI質問テンプレート

> 以下は再実験用に整理した**質問例**であり、当初の会話の完全な原文ではありません。

```text
これは自分で管理する隔離された仮想ネットワークのSSH設定です。
以下の設定値から、想定されるセキュリティリスク、評価に必要な追加情報、
リスクが実在するか確かめるための安全な検証方法、変更候補と注意点を整理してください。
各指摘について「設定から確定できる事実」と「仮説」を分けてください。

port 22
permitrootlogin prohibit-password
pubkeyauthentication yes
passwordauthentication yes

業務上の前提：SSH管理を行う端末はWindows。Kaliは検証用で管理端末ではない。
```

## 検証時の注意

- `PasswordAuthentication yes` や標準ポート22は、それ自体では脆弱性を証明しません。
- 接続タイムアウト単独では原因を特定できないため、pfSenseの該当TCP 22ログと照合します。
- `Connection reset ... [preauth]` だけでパスワード認証拒否とは断定しません。認証方式を限定した試験結果と有効設定を併用します。
- AIによるリスク評価は提案・仮説です。事実確認は通信試験とサーバーログに基づきます。

## 対応する証拠画像

- [初期SSH設定](../images/07-ssh-settings-before.png)
- [対策前のSSHログイン](../images/03-ssh-login-before.png)
- [Kaliの遮断後の結果](../images/05-kali-ssh-blocked.png)
- [pfSenseの許可・遮断ログ](../images/10-pfsense-allow-deny-log.png)
- [SSH有効設定](../images/08-ssh-effective-settings.png)
- [SSH認証ログ](../images/09-authentication-events.png)
