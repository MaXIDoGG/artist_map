#!/usr/bin/env python3
"""Деплой на VPS по SSH. Пароль передавайте через переменную DEPLOY_SSH_PASSWORD."""

from __future__ import annotations

import argparse
import os
import secrets
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
REMOTE_DIR = "/opt/artist_map"
ARCHIVE_SKIP_PREFIXES = (
    ".git/",
    ".env",
    "venv/",
    ".venv/",
    "frontend/node_modules/",
    "frontend/dist/",
    "__pycache__/",
    ".pytest_cache/",
    "data/",
    "backups/",
    "terminals/",
    "agent-transcripts/",
)


def run_local(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def create_archive(target: Path) -> None:
    with tarfile.open(target, "w:gz") as tar:
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            rel_posix = rel.as_posix()
            if any(rel_posix.startswith(prefix) or rel_posix == prefix.rstrip("/") for prefix in ARCHIVE_SKIP_PREFIXES):
                continue
            if rel.suffix in {".pyc", ".sql"}:
                continue
            tar.add(path, arcname=rel.as_posix())


def ssh_connect(host: str, user: str, password: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=60)
    return client


def run_remote(client: paramiko.SSHClient, command: str) -> None:
    print(f"remote$ {command}")
    _, stdout, stderr = client.exec_command(command, get_pty=True)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        safe_out = out.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8",
            errors="replace",
        )
        print(safe_out, end="" if safe_out.endswith("\n") else "\n")
    if err:
        safe_err = err.encode(sys.stderr.encoding or "utf-8", errors="replace").decode(
            sys.stderr.encoding or "utf-8",
            errors="replace",
        )
        print(safe_err, file=sys.stderr, end="" if safe_err.endswith("\n") else "\n")
    if exit_code != 0:
        raise RuntimeError(f"Команда завершилась с кодом {exit_code}: {command}")


def upload_file(sftp: paramiko.SFTPClient, local: Path, remote: str) -> None:
    print(f"upload {local} -> {remote}")
    sftp.put(str(local), remote)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy Artist Map to VPS")
    parser.add_argument("--host", default="31.130.133.28")
    parser.add_argument("--user", default="root")
    parser.add_argument("--skip-dump", action="store_true")
    args = parser.parse_args()

    password = os.environ.get("DEPLOY_SSH_PASSWORD")
    if not password:
        print("Установите DEPLOY_SSH_PASSWORD", file=sys.stderr)
        sys.exit(1)

    backups = ROOT / "backups"
    backups.mkdir(exist_ok=True)
    sql_path = backups / "artist_map.sql"

    if not args.skip_dump:
        with sql_path.open("wb") as sql_file:
            subprocess.run(
                [
                    "docker",
                    "exec",
                    "artist-map-postgres",
                    "pg_dump",
                    "-U",
                    "artist_map",
                    "--no-owner",
                    "--no-acl",
                    "artist_map",
                ],
                cwd=ROOT,
                check=True,
                stdout=sql_file,
            )
        print(f"Дамп: {sql_path} ({sql_path.stat().st_size // 1024} KB)")

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "artist_map.tar.gz"
        create_archive(archive)

        client = ssh_connect(args.host, args.user, password)
        sftp = client.open_sftp()
        try:
            run_remote(client, f"mkdir -p {REMOTE_DIR}/backups")
            upload_file(sftp, archive, f"{REMOTE_DIR}/artist_map.tar.gz")
            if sql_path.exists():
                upload_file(sftp, sql_path, f"{REMOTE_DIR}/backups/artist_map.sql")

            postgres_password = secrets.token_urlsafe(24)
            bootstrap = f"""
set -e
if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl
  curl -fsSL https://get.docker.com | sh
fi
cd {REMOTE_DIR}
tar -xzf artist_map.tar.gz
rm -f artist_map.tar.gz
cat > .env <<'EOF'
ENVIRONMENT=production
POSTGRES_PASSWORD={postgres_password}
DATABASE_URL=postgresql+psycopg://artist_map:{postgres_password}@postgres:5432/artist_map
CORS_ORIGINS=["http://{args.host}"]
YANDEX_MUSIC_TOKEN=
IMPORT_MAX_DEPTH=3
IMPORT_TRACK_PAGE_SIZE=100
GRAPH_CACHE_SECONDS=300
EOF
chmod +x scripts/deploy_server.sh deploy/entrypoint-api.sh
sed -i 's/\\r$//' deploy/entrypoint-api.sh scripts/deploy_server.sh || true
RESTORE_DB=1 bash scripts/deploy_server.sh
"""
            run_remote(client, bootstrap)
        finally:
            sftp.close()
            client.close()

    import time
    import urllib.error
    import urllib.request

    url = f"http://{args.host}/api/v1/health"
    print(f"Проверка {url}")
    for attempt in range(1, 31):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                print(response.read().decode())
            break
        except urllib.error.URLError as error:
            if attempt == 30:
                raise
            print(f"Ожидание API ({attempt}/30): {error}")
            time.sleep(10)


if __name__ == "__main__":
    main()
