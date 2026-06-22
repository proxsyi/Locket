#!/usr/bin/env python3
import json, os, subprocess, sys, urllib.request, urllib.error
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, ".locket")
CONF = os.path.join(ROOT, "locket.conf.json")
LOG = os.path.join(ROOT, "log.txt")
NOTION_VERSION = "2022-06-28"
MAX_LEN = 100
API = "https://api.notion.com/v1"


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def cfg():
    with open(CONF) as f:
        return json.load(f)


def notion(path, c, body):
    req = urllib.request.Request(
        API + path, method="POST",
        headers={
            "Authorization": f"Bearer {c['NOTION_TOKEN']}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        data=json.dumps(body).encode(),
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read())


def live_note(c):
    title_prop = c.get("TITLE_PROP", "Note")
    live_prop = c.get("LIVE_PROP", "Live")
    data = notion("/databases/" + c["DATABASE_ID"] + "/query", c, {
        "filter": {"property": live_prop, "checkbox": {"equals": True}},
        "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
        "page_size": 1,
    })
    results = data.get("results", [])
    if not results:
        return None, None
    page = results[0]
    title = page["properties"][title_prop]["title"]
    text = "".join(t.get("plain_text", "") for t in title).strip()
    return (text or None), page["id"]


def bump_last_shown(c, page_id):
    prop = c.get("LAST_SHOWN_PROP")
    if not prop:
        return
    today = datetime.now(timezone.utc).date().isoformat()
    req = urllib.request.Request(
        API + "/pages/" + page_id, method="PATCH",
        headers={
            "Authorization": f"Bearer {c['NOTION_TOKEN']}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        data=json.dumps({"properties": {prop: {"date": {"start": today}}}}).encode(),
    )
    try:
        urllib.request.urlopen(req, timeout=12).read()
    except Exception as e:
        log(f"warn: could not bump {prop}: {e}")


def write_lockscreen(text):
    subprocess.run([
        "sudo", "-n", "/usr/bin/defaults", "write",
        "/Library/Preferences/com.apple.loginwindow",
        "LoginwindowText", "-string", text[:MAX_LEN],
    ], check=True)


def main():
    try:
        c = cfg()
    except Exception as e:
        log(f"skip: no config: {e}")
        return 0
    try:
        text, page_id = live_note(c)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        log(f"skip: network: {e}")
        return 0
    if not text:
        log("skip: no live note")
        return 0
    try:
        write_lockscreen(text)
    except subprocess.CalledProcessError as e:
        log(f"fail: defaults write: {e}")
        return 1
    bump_last_shown(c, page_id)
    log(f"ok: {text!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
