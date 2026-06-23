#!/usr/bin/env python3
import json, os, re, shutil, subprocess, sys, tarfile, tempfile, urllib.request
from datetime import datetime

HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, ".locket")
LOG = os.path.join(ROOT, "update.log")
LOCK = os.path.join(ROOT, "update.lock")
VERSION_FILE = os.path.join(ROOT, "version")
CURRENT_VERSION = "v0.2.0"
REPO = "proxsyi/Locket"
TAGS_URL = "https://api.github.com/repos/" + REPO + "/tags"


def log(msg):
    os.makedirs(ROOT, exist_ok=True)
    with open(LOG, "a") as f:
        f.write("[" + datetime.now().isoformat() + "] " + msg + "\n")


def version_tuple(v):
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", v.strip())
    if not m:
        return (0, 0, 0)
    return tuple(int(x) for x in m.groups())


def current_version():
    try:
        with open(VERSION_FILE) as f:
            return f.read().strip() or CURRENT_VERSION
    except Exception:
        return CURRENT_VERSION


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Locket"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def latest_tag():
    tags = get_json(TAGS_URL)
    names = [t.get("name", "") for t in tags]
    names = [n for n in names if re.match(r"^v\d+\.\d+\.\d+$", n)]
    if not names:
        return None
    names.sort(key=version_tuple, reverse=True)
    return names[0]


def find_agent_dir(path):
    for name in os.listdir(path):
        candidate = os.path.join(path, name, "agent")
        if os.path.isdir(candidate):
            return candidate
    return None


def install_tag(tag):
    url = "https://codeload.github.com/" + REPO + "/tar.gz/refs/tags/" + tag
    with tempfile.TemporaryDirectory() as tmp:
        archive = os.path.join(tmp, "locket.tar.gz")
        urllib.request.urlretrieve(url, archive)
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(tmp)
        agent_dir = find_agent_dir(tmp)
        if not agent_dir:
            raise RuntimeError("agent directory not found")
        subprocess.run(["/bin/bash", os.path.join(agent_dir, "install.sh"), "--update", tag], check=True)


def acquire_lock():
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


def main():
    if not acquire_lock():
        return 0
    try:
        current = current_version()
        latest = latest_tag()
        if not latest:
            log("skip: no tag found")
            return 0
        if version_tuple(latest) <= version_tuple(current):
            log("ok: current " + current)
            return 0
        log("update: " + current + " -> " + latest)
        install_tag(latest)
        log("updated: " + latest)
        return 0
    except Exception as e:
        log("fail: " + str(e))
        return 0
    finally:
        try:
            os.remove(LOCK)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
