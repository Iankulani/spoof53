# spoof53

Spoof53 is the first unified command-and-control (C2) execution tool designed for red teams, penetration testers, and security researchers who demand operational flexibility without sacrificing stealth. Instead of managing multiple bots, listeners, or proprietary agents across different messaging ecosystems, Spoof53 consolidates everything into a single, lightweight orchestration layer.

With Spoof53, you fire commands from wherever your team already communicates. The tool integrates natively with Telegram, Discord, iMessage, Slack, and Google Chat—allowing operators to issue instructions, retrieve outputs, pivot through networks, or deploy payloads using simple natural language or encrypted command syntax. There is no need to expose legacy C2 infrastructure over HTTP(S) or DNS, drastically reducing the detection footprint.

How it works: You configure the Spoof53 engine on your controller machine, authenticate the desired chat platforms via API tokens, webhooks, or AppleScript bridges (for iMessage), and define your implant communication channels. From that moment on, every connected platform acts as a bidirectional relay. Type /scan 10.0.0.0/24 in a private Telegram group, and Spoof53 forwards it to the correct agent cluster. Receive real‑time results as threaded replies in Slack, as a direct message on Discord, or as an iMessage transcript on your Mac.

Key features include role‑based access control per platform, end‑to‑end encryption for command payloads, session persistence across disconnected clients, and full logging for operational after‑action reviews. Spoof53 also supports channel‑specific command aliases—so a quick !ps in Google Chat can list processes, while the same command typed in iMessage triggers a different agent pool.

Built for evasion and resilience, Spoof53 never stores credentials in plaintext and rotates message formatting patterns to avoid pattern‑based detection. Whether you’re coordinating a five‑person red team exercise or running a solo infrastructure assessment, Spoof53 turns everyday chat apps into your most powerful, invisible C2 backbone. No custom apps. No suspicious domains. Just commands, everywhere you already work.

# How to clone the repo
```bash
git clone https://github.com/Iankulani/spoof53.git
cd spoof53
```

# How to run 
  ```bash
python spoof53.py
```
