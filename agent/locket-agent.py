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
        f.write("[" + datetime.now().isoformat() + "] " + msg + "\n")


def cfg():
    with open(CONF) as f:
        return json.load(f)


def api(path, c, method, body):
    req = urllib.request.Request(
        API + path, method=method,
        headers={
            "Authorization": "Bearer " + c["NOTION_TOKEN"],
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        data=json.dumps(body).encode(),
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read())


def set_live(c, page_id, value):
    live_prop = c.get("LIVE_PROP", "Live")
    api("/pages/" + page_id, c, "PATCH", {"properties": {live_prop: {"checkbox": value}}})


def resolve_live(c):
    title_prop = c.get("TITLE_PROP", "Note")
    live_prop = c.get("LIVE_PROP", "Live")
    last_prop = c.get("LAST_SHOWN_PROP")
    data = api("/databases/" + c["DATABASE_ID"] + "/query", c, "POST", {
        "filter": {"property": live_prop, "checkbox": {"equals": True}},
        "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
        "page_size": 100,
    })
    live = data.get("results", [])
    if len(live) > 1:
        for page in live[1:]:
            try:
                set_live(c, page["id"], False)
            except Exception as e:
                log("warn: could not uncheck extra live: " + str(e))
        live = live[:1]
    if not live:
        if last_prop:
            sorts = [{"property": last_prop, "direction": "ascending"}]
        else:
            sorts = [{"timestamp": "created_time", "direction": "ascending"}]
        pick = api("/databases/" + c["DATABASE_ID"] + "/query", c, "POST", {"sorts": sorts, "page_size": 1})
        results = pick.get("results", [])
        if not results:
            return None, None
        page = results[0]
        try:
            set_live(c, page["id"], True)
        except Exception as e:
            log("warn: could not auto-check fallback: " + str(e))
        live = [page]
    page = live[0]
    title = page["properties"][title_prop]["title"]
    text = "".join(t.get("plain_text", "") for t in title).strip()
    return (text or None), page["id"]


def bump_last_shown(c, page_id):
    prop = c.get("LAST_SHOWN_PROP")
    if not prop:
        return
    today = datetime.now(timezone.utc).date().isoformat()
    try:
        api("/pages/" + page_id, c, "PATCH", {"properties": {prop: {"date": {"start": today}}}})
    except Exception as e:
        log("warn: could not bump " + prop + ": " + str(e))


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
        log("skip: no config: " + str(e))
        return 0
    try:
        text, page_id = resolve_live(c)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        log("skip: network: " + str(e))
        return 0
    if not text:
        log("skip: database empty")
        return 0
    try:
        write_lockscreen(text)
    except subprocess.CalledProcessError as e:
        log("fail: defaults write: " + str(e))
        return 1
    bump_last_shown(c, page_id)
    log("ok: " + repr(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
