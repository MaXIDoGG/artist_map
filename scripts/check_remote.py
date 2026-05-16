import os
import sys
import urllib.request

import paramiko

host = sys.argv[1] if len(sys.argv) > 1 else "31.130.133.28"
password = os.environ["DEPLOY_SSH_PASSWORD"]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username="root", password=password, timeout=30)

for cmd in (
    "cd /opt/artist_map && docker compose -f docker-compose.prod.yml ps",
    "curl -s http://127.0.0.1/api/v1/health",
):
    print("===", cmd)
    _, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(err, file=sys.stderr)

client.close()

url = f"http://{host}/api/v1/health"
print("=== external", url)
print(urllib.request.urlopen(url, timeout=15).read().decode())
