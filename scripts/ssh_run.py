import os
import sys

import paramiko

password = os.environ["DEPLOY_SSH_PASSWORD"]
host = sys.argv[1] if len(sys.argv) > 1 else "31.130.133.28"
command = sys.argv[2]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username="root", password=password, timeout=30)
_, stdout, stderr = client.exec_command(command, get_pty=True)
print(stdout.read().decode("utf-8", errors="replace"))
err = stderr.read().decode("utf-8", errors="replace")
if err:
    print(err, file=sys.stderr)
print("exit", stdout.channel.recv_exit_status())
client.close()
