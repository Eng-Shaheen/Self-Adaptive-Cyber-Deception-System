#!/usr/bin/env python3
"""
AI Decision Engine (Enhanced — canonical file path + diversified output)
"""

import os
import json
import time
import hashlib
import datetime
import random
import mimetypes
import string
import sys
import secrets

BASE_DIR = os.path.expanduser("~/FYP-Project/code/ai_module")
INPUT = os.path.join(BASE_DIR, "inputs", "incoming_event.json")
OUTPUT_LOG = os.path.join(BASE_DIR, "outputs", "deception_responses.log")
DECISIONS = os.path.join(BASE_DIR, "logs/ai_decisions.jsonl")

PROJECT_ROOT = os.environ.get("FYP_PROJECT_ROOT", os.path.expanduser("~/FYP-Project"))
AI_GEN_DIR = os.path.join(PROJECT_ROOT, "assets", "ai_generated")
os.makedirs(AI_GEN_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DECISIONS), exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_LOG), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "inputs"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "outputs"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

AI_MODE = os.environ.get("FYP_AI_MODE", "local")

PROMPTS = {
    "auth.failed": [
        "Generate a believable admin note referencing account lockouts and remediation steps.",
        "Create a fake internal email snippet discussing API keys rotated after failed logins.",
        "Produce an incident summary describing repeated failed login attempts and suggested actions."
    ],
    "session.connect": [
        "Generate fake command output showing system info and a hidden note in a log.",
        "Create a system README snippet that hints at a dev-secret file location.",
        "Produce a sample process list showing an unusual daemon and a comment about sudo usage."
    ],
    "port.scan": [
        "Craft a misleading service configuration file and a short changelog indicating legacy services.",
        "Produce a fake nmap-style summary log indicating closed and filtered ports with annotations."
    ],
    "default": [
        "Produce a short admin note about system maintenance and dummy contact details.",
        "Create a developer TODO entry referencing rotated keys and an archival hint."
    ]
}

def now_iso_ts():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def now_readable_ts():
    return datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

def safe_response(text):
    if text is None:
        return ""
    banned = ["password", "ssh-rsa", "-----BEGIN", "secretkey", "PRIVATE", "PRIVATE KEY"]
    s = str(text)
    for b in banned:
        if b.lower() in s.lower():
            return "[REDACTED: sensitive content]"
    return s

def read_event():
    try:
        with open(INPUT, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None

def random_token(n=8):
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(n))

def make_event_id():
    return "evt-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def random_template(eventid):
    tpl_dir = os.path.expanduser("~/FYP-Project/config/templates")
    try:
        files = [f for f in os.listdir(tpl_dir) if f.endswith(".tpl")]
        if files:
            chosen = random.choice(files)
            tpl_path = os.path.join(tpl_dir, chosen)
            try:
                with open(tpl_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except Exception:
                content = ""
            return chosen, content
    except Exception:
        pass
    fallback_text = PROMPTS.get(eventid, PROMPTS["default"])[0]
    return "builtin", fallback_text

def local_generate(event):
    evt = event or {}
    incoming_eventid = evt.get("eventid") or evt.get("event_id") or make_event_id()
    tpl_name, tpl_content = random_template(incoming_eventid)
    nonce = random_token(6)
    gen_id = hashlib.md5((str(evt.get("src_ip", "")) + nonce + str(time.time())).encode()).hexdigest()[:8]

    tsstamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    safe_ip = str(evt.get("src_ip", "unknown")).replace(":", "-").replace("/", "-")
    base_name = f"create_decoy_file_{safe_ip}_{tsstamp}_{gen_id}.txt"
    file_path = os.path.join(AI_GEN_DIR, base_name)

    chosen_prompts = PROMPTS.get(incoming_eventid)
    if not chosen_prompts:
        etype = (evt.get("event") or evt.get("type") or "").lower()
        if "auth" in etype or "login" in etype or "failed" in etype:
            chosen_prompts = PROMPTS["auth.failed"]
        elif "session" in etype or "connect" in etype:
            chosen_prompts = PROMPTS["session.connect"]
        elif "scan" in etype or "port" in etype:
            chosen_prompts = PROMPTS["port.scan"]
        else:
            chosen_prompts = PROMPTS["default"]

    prompt_choice = random.choice(chosen_prompts)

    random_suffix = random.choice(["#", "//", "--", "!!"])
    variation_tag = f"{random_suffix}{random.randint(10,999)}"
    confidence_score = round(random.uniform(0.72, 0.96), 2)
    lure_hint = random.choice([
        "admin.conf.bak", "db_backup.old", "dev_notes.md",
        "network_config.ini", "archived_users.csv", "ssh_known_hosts.tmp"
    ])

    content_lines = []
    content_lines.append(f"// Generated (local stub) at {now_iso_ts()} {variation_tag}")
    content_lines.append(f"PROMPT: {prompt_choice}")
    content_lines.append("-- SAMPLE LURE CONTENT --")

    if "auth" in (evt.get("eventid","") or "").lower() or "login" in (evt.get("event","") or "").lower():
        content_lines.append(f"Temporary access token: TOK-{hashlib.sha1((safe_ip + gen_id).encode()).hexdigest()[:8]}")
        content_lines.append("Note: Rotate after use.")
        contact = random.choice(["it-admin@corp.local", "infra-team@corp.local", "sec-team@corp.local"])
        content_lines.append(f"Contact: {contact}")
    else:
        content_lines.append(f"Readme hint: /home/admin/{lure_hint}")
        content_lines.append("Note: this is a simulated lure.")
        content_lines.append(f"Reference ID: {hashlib.sha1((str(time.time()) + gen_id).encode()).hexdigest()[:6]}")

    generated_text = "\n".join(content_lines)
    engage_duration_min = round(random.uniform(1.0, 15.0), 2)

    meta = {
        "gen_id": gen_id,
        "nonce_hash": hashlib.sha1(nonce.encode()).hexdigest()[:8],
        "template_file": tpl_name,
        "file_name": base_name,
        "file_path": file_path,
        "file_size_bytes": None,
        "owner_uid": os.getuid(),
        "mtime": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "mime": mimetypes.guess_type(base_name)[0] or "text/plain",
        "engage_duration_min": engage_duration_min
    }

    resp = {
        "text": generated_text,
        "mode": "local",
        "prompt": prompt_choice,
        "confidence": confidence_score,
        "meta": meta,
        "selected_action": "create_decoy_file",
        "incoming_eventid": incoming_eventid
    }
    return resp

def api_generate(event):
    try:
        import openai
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        base_prompt = f"You are a cybersecurity deception assistant. Generate a harmless, believable internal artifact. Event: {event}"
        ai_output = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate harmless deception artifacts. No secrets."},
                {"role": "user", "content": base_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        text = ai_output["choices"][0]["message"]["content"]
        resp = local_generate(event)
        resp["text"] = safe_response(text)
        resp["mode"] = "api"
        resp["prompt"] = "genai-openai"
        resp["confidence"] = 0.90
        return resp
    except Exception:
        return local_generate(event)

def write_decision(event, resp):
    incoming_eventid = event.get("eventid") or event.get("event_id") or resp.get("incoming_eventid") or make_event_id()
    decision_id = "dec-" + secrets.token_hex(4)
    readable_ts = now_readable_ts()
    meta = resp.get("meta", {})
    meta.setdefault("gen_id", hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
    meta.setdefault("file_path", "")
    meta.setdefault("engage_duration_min", round(random.uniform(1.0, 15.0),2))
    meta.setdefault("template_file", "builtin")

    rec = {
        "timestamp": readable_ts,
        "timestamp_iso": now_iso_ts(),
        "eventid": incoming_eventid,
        "decision_id": decision_id,
        "src_ip": event.get("src_ip"),
        "response_mode": resp.get("mode"),
        "response": safe_response(resp.get("text")),
        "prompt": resp.get("prompt"),
        "selected_action": resp.get("selected_action") or "create_decoy_file",
        "confidence": resp.get("confidence", 0.85),
        "meta": meta
    }

    try:
        with open(DECISIONS, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception as e:
        print("Error writing decisions:", e)

    try:
        with open(OUTPUT_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, indent=2) + "\n")
    except Exception as e:
        print("Error writing output log:", e)

    print("AI Decision logged:")
    print(json.dumps(rec, indent=2))
    return rec

def main():
    ev = read_event()
    if not ev:
        print("No event found; exiting.")
        return
    if AI_MODE == "local":
        resp = local_generate(ev)
    else:
        resp = api_generate(ev)
    resp_meta = resp.get("meta", {})
    resp_meta.setdefault("selected_action", resp.get("selected_action", "create_decoy_file"))
    resp["meta"] = resp_meta
    write_decision(ev, resp)

if __name__ == "__main__":
    main()
