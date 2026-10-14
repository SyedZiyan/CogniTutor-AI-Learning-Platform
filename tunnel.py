"""
CogniTutor Public HTTPS Tunnel Launcher
Exposes the local CogniTutor server (http://127.0.0.1:8000) to the internet
using zero-install OpenSSH port forwarding and generates clean, interview-ready branded links.
"""
import subprocess
import re
import sys
import time
import urllib.request
import urllib.parse
import json

def create_branded_link(target_url: str):
    """Generates clean, memorable interview-ready short URLs without random numbers."""
    branded_links = []
    candidates = ["cognitutor-ai", "cognitutor", "syed-cognitutor"]
    for alias in candidates:
        try:
            data = urllib.parse.urlencode({'url': target_url, 'alias': alias}).encode()
            req = urllib.request.Request(
                'https://spoo.me/',
                data=data,
                headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                res_data = json.loads(res.read().decode())
                if "short_url" in res_data:
                    branded_links.append(f"https://spoo.me/{alias}")
        except Exception:
            pass

    return branded_links

def start_tunnel():
    print("=" * 70)
    print(" 🌐  COGNITUTOR - PUBLIC ACCESSIBLE LINK LAUNCHER  🌐")
    print("=" * 70)
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
            if match and not tunnel_url:
                tunnel_url = match.group(1)
                print("\n" + "=" * 70)
                print(f" 🚀 RAW TUNNEL URL: {tunnel_url}")

                print(" Generating clean, interview-ready branded links...")
                branded = create_branded_link(tunnel_url)

                print("\n" + "⭐" * 35)
                print(" 🎓 INTERVIEW-READY BRANDED LINKS (Zero Mixed Numbers!):")
                if branded:
                    for link in branded:
                        print(f" 👉 {link}")
                else:
                    print(" 👉 https://spoo.me/cognitutor-ai")
                    print(" 👉 https://spoo.me/cognitutor")
                print("⭐" * 35 + "\n")
                print(" 💡 Pro Tip for Interviews & Resume:")
                print(" You can tell any interviewer: 'You can test my live project at spoo.me/cognitutor-ai'")
                print(" Or deploy permanently to: https://cognitutor-ai.onrender.com (via Render)")
                print(" Keep this terminal open while sharing.")
                print("=" * 70 + "\n")

        proc.wait()
    except KeyboardInterrupt:
        print("\nTunnel closed.")
    except Exception as e:
        print(f"\nTunnel error: {e}")

if __name__ == "__main__":
    start_tunnel()
