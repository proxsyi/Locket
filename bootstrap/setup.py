#!/usr/bin/env python3
import json, os, re, shutil, sys, tarfile, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT_SRC = os.path.join(os.path.dirname(HERE), "agent")
OUT_DIR = os.path.join(HERE, "locket-partner")
TARBALL = os.path.join(HERE, "locket-partner.tar.gz")
NOTION_VERSION = "2022-06-28"
API = "https://api.notion.com/v1"


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    s = input(f"{prompt}{suffix}: ").strip()
    return s or (default or "")


def clean_db_id(raw):
    raw = raw.strip().replace("-", "")
    m = re.search(r"([0-9a-fA-F]{32})", raw)
    return m.group(1) if m else raw


def verify(token, db_id):
    req = urllib.request.Request(
        API + "/databases/" + db_id + "/query", method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        data=json.dumps({"page_size": 1}).encode(),
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        json.loads(r.read())
    return True


def build_partner_pkg(conf):
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)
    for f in ("locket-agent.py", "locket-update.py", "install.sh", "uninstall.sh", "README.md", "VERSION"):
        shutil.copy(os.path.join(AGENT_SRC, f), os.path.join(OUT_DIR, f))
    conf_path = os.path.join(OUT_DIR, "locket.conf.json")
    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    os.chmod(conf_path, 0o600)
    if os.path.exists(TARBALL):
        os.remove(TARBALL)
    with tarfile.open(TARBALL, "w:gz") as tar:
        tar.add(OUT_DIR, arcname="locket-partner")
    return TARBALL


def main():
    print("")
    print("Locket setup")
    print("")
    token = ask("Notion integration token (secret_... or ntn_...)")
    db_id = clean_db_id(ask("Locket database ID or URL"))
    print("")
    print("Verifying with Notion...")
    try:
        verify(token, db_id)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"Could not reach that database: {e}")
        print("Check the token, the database id, and that the database is")
        print("shared with the integration under its Connections menu.")
        return 1
    print("Verified.")
    print("")
    conf = {
        "NOTION_TOKEN": token,
        "DATABASE_ID": db_id,
        "TITLE_PROP": ask("Title property name", "Note"),
        "LIVE_PROP": ask("Live checkbox property name", "Live"),
        "LAST_SHOWN_PROP": ask("Last Shown date property (blank to skip)", "Last Shown"),
    }
    if not conf["LAST_SHOWN_PROP"]:
        conf.pop("LAST_SHOWN_PROP")
    tarball = build_partner_pkg(conf)
    ip = ask("Partner Mac user@ip (blank to skip the ready command)", "")
    base = os.path.basename(tarball)
    print("")
    print(f"Built: {tarball}")
    print("")
    print("Send it over, then have them run install.sh once:")
    print("")
    if ip:
        print("  scp " + base + " " + ip + ":~/")
        print("  ssh " + ip + " 'tar xzf " + base + " && cd locket-partner && ./install.sh'")
    else:
        print("  scp " + base + " USER@THEIR_IP:~/")
        print("  ssh USER@THEIR_IP 'tar xzf " + base + " && cd locket-partner && ./install.sh'")
    print("")
    print("  or AirDrop or USB the tarball and run ./install.sh on their machine.")
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
