"""
CogniTutor Public HTTPS Tunnel Launcher
Exposes the local CogniTutor server (http://127.0.0.1:8000) to the internet
using zero-install OpenSSH port forwarding.
"""
import subprocess
import re
import sys
import time

def start_tunnel():
    print("=" * 65)
    print(" 🌐  COGNITUTOR - PUBLIC ACCESSIBLE LINK LAUNCHER  🌐")
    print("=" * 65)
    print(" Connecting to secure HTTPS reverse tunnel...")

    ssh_cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-R", "80:127.0.0.1:8000",
        "nokey@localhost.run"
    ]

    try:
        proc = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        tunnel_url = None
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

            match = re.search(r'(https://[a-zA-Z0-9\-\.]+\.lhr\.life)', line)
            if match:
                tunnel_url = match.group(1)
                print("\n" + "*" * 65)
                print(f" 🚀 YOUR PUBLIC COGNITUTOR URL IS LIVE:")
                print(f" 👉 {tunnel_url}")
                print("*" * 65 + "\n")
                print("Share this link with anyone - accessible on mobile & PC worldwide.")
                print("Keep this window open to maintain the connection.\n")

        proc.wait()
    except KeyboardInterrupt:
        print("\nTunnel closed.")
    except Exception as e:
        print(f"\nTunnel error: {e}")

if __name__ == "__main__":
    start_tunnel()
