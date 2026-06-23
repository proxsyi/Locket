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


def api(path, c, method, body=None):
    data = None
    if body is not None:
        data = json.dumps(body).encode()
    req = urllib.request.Request(
        API + path, method=method,
        headers={
            "Authorization": "Bearer " + c["NOTION_TOKEN"],
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        data=data,
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read())


def query(c, body):
    return api("/databases/" + c["DATABASE_ID"] + "/query", c, "POST", body).get("results", [])


def text_for(c, page):
    title_prop = c.get("TITLE_PROP", "Note")
    prop = page.get("properties", {}).get(title_prop, {})
    title = prop.get("title", [])
    text = "".join(t.get("plain_text", "") for t in title).strip()
    return text or None


def set_live(c, page_id, value):
    live_prop = c.get("LIVE_PROP", "Live")
    api("/pages/" + page_id, c, "PATCH", {"properties": {live_prop: {"checkbox": value}}})


def normalize_live(c):
    live_prop = c.get("LIVE_PROP", "Live")
    live = query(c, {
        "filter": {"property": live_prop, "checkbox": {"equals": True}},
        "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
        "page_size": 100,
    })
    if len(live) > 1:
        for page in live[1:]:
            try:
                set_live(c, page["id"], False)
            except Exception as e:
                log("warn: could not uncheck extra live: " + str(e))
        live = live[:1]
    if live:
        return live[0]
    return None


def sorted_notes(c):
    last_prop = c.get("LAST_SHOWN_PROP")
    if last_prop:
        sorts = [{"property": last_prop, "direction": "ascending"}]
    else:
        sorts = [{"timestamp": "created_time", "direction": "ascending"}]
    return query(c, {"sorts": sorts, "page_size": 100})


def resolve_live(c):
    page = normalize_live(c)
    if page is None:
        notes = sorted_notes(c)
        if not notes:
            return None, None
        page = notes[0]
        try:
            set_live(c, page["id"], True)
        except Exception as e:
            log("warn: could not auto-check fallback: " + str(e))
    return text_for(c, page), page["id"]


def rotate_live(c):
    current = normalize_live(c)
    notes = sorted_notes(c)
    if not notes:
        return None, None
    current_id = current.get("id") if current else None
    pick = None
    for page in notes:
        if page.get("id") != current_id:
            pick = page
            break
    if pick is None:
        pick = current or notes[0]
    if current_id != pick.get("id"):
        if current_id:
            try:
                set_live(c, current_id, False)
            except Exception as e:
                log("warn: could not uncheck previous live: " + str(e))
        try:
            set_live(c, pick["id"], True)
        except Exception as e:
            log("warn: could not check rotated live: " + str(e))
    return text_for(c, pick), pick["id"]


def bump_last_shown(c, page_id):
    prop = c.get("LAST_SHOWN_PROP")
    if not prop:
        return
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        api("/pages/" + page_id, c, "PATCH", {"properties": {prop: {"date": {"start": now}}}})
    except Exception as e:
        log("warn: could not bump " + prop + ": " + str(e))


def write_lockscreen(text):
    subprocess.run([
        "sudo", "-n", "/usr/bin/defaults", "write",
        "/Library/Preferences/com.apple.loginwindow",
        "LoginwindowText", "-string", text[:MAX_LEN],
    ], check=True)


def main():
    mode = "sync"
    if len(sys.argv) > 1 and sys.argv[1] == "--rotate":
        mode = "rotate"
    try:
        c = cfg()
    except Exception as e:
        log("skip: no config: " + str(e))
        return 0
    try:
        if mode == "rotate":
            text, page_id = rotate_live(c)
        else:
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
    log("ok " + mode + ": " + repr(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
