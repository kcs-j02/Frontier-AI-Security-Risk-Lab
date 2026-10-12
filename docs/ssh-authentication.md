# Ubuntu SSH公開鍵認証への移行

> 対策案の追加検証として行った認証強化。実際のCRX製品を利用した結果ではありません。

## 手順（実施内容）

1. Windows上で `ssh-keygen -t ed25519` により鍵ペアを生成（秘密鍵はWindows内に保持）。
2. 公開鍵のみをUbuntuユーザー `csirt` の `~/.ssh/authorized_keys` に登録。
3. 公開鍵認証限定のSSH接続が成功することを確認。
4. Ubuntuの `/etc/ssh/sshd_config.d/50-cloud-init.conf` を `PasswordAuthentication no` に変更。
5. `sudo sshd -t` で構文検証。`sudo sshd -T` で有効設定を確認し、SSHサービスを再起動。
6. Windowsから公開鍵認証のみの接続に成功。パスワード方式のみの接続試験ではログイン拒否を確認。

有効設定の確認結果:

```text
pubkeyauthentication yes
passwordauthentication no
kbdinteractiveauthentication no
```

![Effective SSH settings and listening socket](../images/08-ssh-effective-settings.png)

## ログの照合

Ubuntuで `sudo journalctl -u ssh.service --no-pager` 等を実行。取得したログから次のような事実を確認しました。

| ログ日時（Ubuntu側表示） | 内容 | 接続元 |
|---|---|---|
| Oct 12 16:47:32 | `Accepted password for csirt` | 192.168.2.100 |
| Oct 12 16:52:33, 17:10:00 | `Accepted password for csirt` | 192.168.1.102 |
| Oct 12 17:13:10, 17:14:48, 17:24:14 | `Accepted publickey for csirt` | 192.168.1.102 |
| Oct 12 17:24:57 | `Connection reset ... [preauth]` | 192.168.1.102 |

重要: `Connection reset ... [preauth]` は認証前に接続が終了したことを示します。**この1行だけではパスワード認証がサーバー側で拒否されたか、クライアントが切断したかは確定できません**。拒否の判断は、別途実施した「パスワードのみの接続試験」と、有効設定 `passwordauthentication no` を併せて評価しています。

![Auth logs](../images/09-authentication-events.png)

## 運用上の注意

公開鍵認証が確実に機能することを確認してからパスワード認証を停止し、変更中はUbuntuのコンソールを確保しました。実運用では鍵の紛失時の復旧手段も必要です。
