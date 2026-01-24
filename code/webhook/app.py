#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string
import json, datetime, os, subprocess, collections, html, time

app = Flask(__name__)

BASE = os.path.expanduser("~/FYP-Project")
AI_DECISIONS = os.path.join(BASE, "code/ai_module/logs/ai_decisions.jsonl")
RECEIVED_LOGS = os.path.join(BASE, "code/webhook/received_logs.json")
DECOY_ACTIONS = os.path.join(BASE, "code/executor/decoy_actions.jsonl")
AI_GEN_DIR = os.path.join(BASE, "assets/ai_generated")

os.makedirs(os.path.dirname(AI_DECISIONS), exist_ok=True)
os.makedirs(os.path.dirname(RECEIVED_LOGS), exist_ok=True)
os.makedirs(os.path.dirname(DECOY_ACTIONS), exist_ok=True)
os.makedirs(AI_GEN_DIR, exist_ok=True)

def tail_lines(path, n=200):
    try:
        with open(path) as fh:
            lines = list(collections.deque(fh, n))
            return [l.rstrip("\n") for l in lines]
    except FileNotFoundError:
        return []

def safe_json(line):
    try:
        return json.loads(line)
    except Exception:
        return None

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def normalize_path_for_host(path):
    if not path:
        return None
    path = str(path)
    if path.startswith("/root/FYP-Project"):
        return path.replace("/root/FYP-Project", BASE)
    if path.startswith("/home/kali/FYP-Project"):
        return path.replace("/home/kali/FYP-Project", BASE)
    return path

def load_decoy_actions_index():
    out = {}
    lines = tail_lines(DECOY_ACTIONS, 1000)
    for ln in lines:
        obj = safe_json(ln)
        if not obj:
            continue
        f = obj.get("file")
        if f:
            out[f] = obj
        gen = obj.get("gen_id")
        if gen:
            out[gen] = obj
    return out

@app.route("/cowrie-log", methods=["POST"])
def receive_log():
    try:
        data = request.get_json(force=True)
        ts = now_iso()
        with open(RECEIVED_LOGS, "a") as f:
            f.write(json.dumps({"timestamp": ts, "data": data}) + "\n")

        ai_input = os.path.join(BASE, "code/ai_module/inputs/incoming_event.json")
        os.makedirs(os.path.dirname(ai_input), exist_ok=True)
        with open(ai_input, "w") as f:
            json.dump(data, f)

        subprocess.run(
            ["python3", os.path.join(BASE, "code/ai_module/generate_deception_action.py")],
            check=False,
        )
        return jsonify({"status": "success", "message": "AI action triggered"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>🧠 Self-Adaptive Cyber Deception Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root { --bg:#f6f9fb; --panel:#fff; --accent:#0b6e86; --accent-2:#2b9bd7; --muted:#536b78; --text:#072029; }
body { margin:0; font-family:"Segoe UI", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial; background:var(--bg); color:var(--text); font-size:16px; }
header { background: linear-gradient(90deg,var(--accent),var(--accent-2)); color:#fff; padding:20px 24px; font-size:2.2rem; font-weight:700; text-align:center; letter-spacing:0.4px; }
.wrap { padding:20px; display:flex; flex-direction:column; gap:18px; }
.summary { display:flex; gap:20px; justify-content:space-around; font-size:1.25rem; color:var(--accent); }
.panel { background:var(--panel); border-radius:10px; padding:16px; box-shadow:0 6px 18px rgba(43,155,215,0.08); }
h3 { margin:0 0 12px 0; color:var(--accent-2); font-size:1.25rem; }
table { width:100%; border-collapse:collapse; font-size:1.05rem; }
th, td { padding:12px 10px; text-align:left; color:var(--text); }
th { background:transparent; color:var(--accent); font-weight:700; position:sticky; top:0; z-index:2; }
tr { border-bottom:1px solid rgba(43,155,215,0.06); }
tr:hover { background:rgba(43,155,215,0.035); cursor:pointer; }
.muted { color:var(--muted); font-size:0.98rem; }
.modal { display:none; position:fixed; z-index:999; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); overflow:auto; }
.modal-content { max-width:900px; margin:40px auto; background:#fff; border-radius:10px; padding:20px; color:#072029; overflow:auto; }
.modal-row { display:flex; gap:18px; flex-wrap:wrap; margin-bottom:8px; }
.modal-row b { min-width:140px; display:inline-block; color:var(--accent); }
pre { background:#f3f7fa; padding:14px; border-radius:8px; color:#072029; white-space:pre-wrap; word-break:break-word; border:1px solid rgba(43,155,215,0.08); font-size:0.98rem; }
.close { float:right; color:var(--accent); cursor:pointer; font-size:1.6rem; }
.note { color:var(--muted); font-size:0.98rem; margin-top:8px; }
</style>
</head>
<body>
<header>🧠 Self-Adaptive Cyber Deception Dashboard (Presentation Mode)</header>
<div class="wrap">
  <div class="summary">
    <div>Received: <span id="rec-count">0</span></div>
    <div>AI Decisions: <span id="ai-count">0</span></div>
    <div>Decoy Actions: <span id="decoy-count">0</span></div>
  </div>
  <div class="panel">
    <h3>Recent AI Decisions</h3>
    <div style="overflow:auto; max-height:420px;">
      <table id="decision-table" aria-live="polite">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Source IP</th>
            <th>Event ID</th>
            <th>AI Action</th>
            <th>Engage Duration (min)</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody><tr><td colspan="6" class="muted">Loading...</td></tr></tbody>
      </table>
    </div>
  </div>
</div>

<div id="modal" class="modal" onclick="if(event.target===this) hideModal()">
  <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <span class="close" onclick="hideModal()">✕</span>
    <h2 id="modal-title">Decision Details</h2>
    <div id="modal-body">Loading...</div>
    <div class="note">Preview limited to first 2000 characters. Files outside the assets folder are blocked for safety.</div>
  </div>
</div>

<footer>© 2025 — Use arrow keys to navigate the table rows. Click a row to inspect details.</footer>

<script>
async function loadData(){
  try {
    const res = await fetch('/api/metrics');
    const data = await res.json();
    document.getElementById('rec-count').textContent = data.counts.received;
    document.getElementById('ai-count').textContent = data.counts.ai;
    document.getElementById('decoy-count').textContent = data.counts.actions;

    const tbody = document.querySelector('#decision-table tbody');
    tbody.innerHTML = '';
    const decisions = data.decisions;
    if(!decisions || decisions.length===0){
      tbody.innerHTML = '<tr><td colspan="6" class="muted">No AI decisions yet</td></tr>';
      return;
    }

    for(const dec of decisions){
      const tr = document.createElement('tr');
      tr.tabIndex = 0;
      tr.innerHTML = `<td>${dec.timestamp||''}</td><td>${dec.src_ip||''}</td><td>${dec.eventid||''}</td><td>${dec.selected_action||''}</td><td>${(dec.engage_duration_min||'-')}</td><td>${(dec.confidence||0).toFixed(2)}</td>`;
      tr.onclick = () => showDetails(dec);
      tr.onkeydown = (e) => { if(e.key === 'Enter') showDetails(dec); };
      tbody.appendChild(tr);
    }
  } catch (e) { console.error("loadData error", e); }
}

function showDetails(dec){
  const body = document.getElementById('modal-body');
  const m = dec.meta || {};
  const file_path = m.file_path || (dec.file || m.file || '-');
  const file_size = m.file_size_bytes || dec.file_size || (dataFromActions(dec) || {}).file_size_bytes || '-';
  const engage = dec.engage_duration_min || '-';
  body.innerHTML = `<div class="modal-row"><b>Event:</b> ${dec.eventid || '-'}</div>
  <div class="modal-row"><b>Src IP:</b> ${dec.src_ip || '-'}</div>
  <div class="modal-row"><b>Action:</b> ${dec.selected_action || '-'}</div>
  <div class="modal-row"><b>Template:</b> ${m.template_file || '-'}</div>
  <div class="modal-row"><b>File path:</b> ${file_path || '-'}</div>
  <div class="modal-row"><b>File size:</b> ${file_size} bytes</div>
  <div class="modal-row"><b>Engage Duration (min):</b> ${engage}</div>
  <div class="modal-row"><b>Gen ID:</b> ${m.gen_id || '-'}</div>
  <div class="modal-row"><b>Confidence:</b> ${(dec.confidence||'-')}</div>
  <hr/><div><b>AI Prompt / Response (raw):</b></div><pre>${(dec.response||'(no response)')}</pre>
  <hr/><div><b>Decoy file preview:</b></div><div id="preview">Loading preview...</div>`;

  if(file_path && file_path !== '-' ){
    fetch('/api/preview?path=' + encodeURIComponent(file_path))
      .then(r => r.json())
      .then(obj => {
        if(obj.content) document.getElementById('preview').innerHTML = '<pre>' + obj.content + '</pre>';
        else if(obj.error) document.getElementById('preview').innerHTML = '<div class="muted">' + obj.error + '</div>';
        else document.getElementById('preview').innerHTML = '<div class="muted">(empty)</div>';
      }).catch(e=>{
        document.getElementById('preview').innerHTML = '<div class="muted">Preview fetch error</div>';
      });
  } else {
    document.getElementById('preview').innerHTML = '<div class="muted">No file path available for preview</div>';
  }
  document.getElementById('modal').style.display = 'block';
}

function hideModal(){ document.getElementById('modal').style.display = 'none'; }

let lastActionsIndex = {};
async function refreshActionsIndex(){
  try {
    const res = await fetch('/api/decoy_index');
    const j = await res.json();
    lastActionsIndex = j || {};
  } catch(e){}
}

function dataFromActions(dec){
  const gen = (dec.meta||{}).gen_id;
  if(gen && lastActionsIndex[gen]) return lastActionsIndex[gen];
  const fp = (dec.meta||{}).file_path;
  if(fp && lastActionsIndex[fp]) return lastActionsIndex[fp];
  return null;
}

setInterval(()=>{ loadData(); refreshActionsIndex(); }, 10000);
loadData();
refreshActionsIndex();
</script>
</body>
</html>"""

@app.route("/api/metrics")
def metrics():
    rec_lines = tail_lines(RECEIVED_LOGS, 200)
    dec_lines = tail_lines(AI_DECISIONS, 200)
    act_lines = tail_lines(DECOY_ACTIONS, 200)

    rec = [safe_json(x) for x in rec_lines if x]
    dec = [safe_json(x) for x in dec_lines if x]
    acts = [safe_json(x) for x in act_lines if x]

    actions_index = {}
    for a in acts:
        if not a:
            continue
        fp = a.get("file")
        if fp: actions_index[fp] = a
        gen = a.get("gen_id")
        if gen: actions_index[gen] = a

    enriched_decisions = []
    for d in dec:
        if not d: continue
        meta = d.get("meta", {}) or {}
        file_path = normalize_path_for_host(meta.get("file_path") or "")
        linked = None
        if file_path and file_path in actions_index:
            linked = actions_index[file_path]
        elif meta.get("gen_id") and meta.get("gen_id") in actions_index:
            linked = actions_index[meta.get("gen_id")]

        if linked:
            if not meta.get("file_size_bytes"):
                meta["file_size_bytes"] = linked.get("file_size_bytes")
            if not meta.get("engage_duration_min"):
                meta["engage_duration_min"] = linked.get("engage_duration_min")

        if meta.get("file_path"):
            meta["file_path"] = normalize_path_for_host(meta["file_path"])

        d["meta"] = meta
        d["timestamp"] = d.get("timestamp") or meta.get("timestamp")
        d["engage_duration_min"] = meta.get("engage_duration_min")
        enriched_decisions.append(d)

    out = {
        "counts": {
            "received": len(rec),
            "ai": len(enriched_decisions),
            "actions": len(acts),
        },
        "decisions": enriched_decisions[::-1][:200],
        "received": rec[::-1][:200],
    }
    return jsonify(out)

@app.route("/api/decoy_index")
def decoy_index():
    acts = tail_lines(DECOY_ACTIONS, 1000)
    idx = {}
    for ln in acts:
        obj = safe_json(ln)
        if not obj: continue
        fp = obj.get("file")
        if fp: idx[fp] = obj
        gen = obj.get("gen_id")
        if gen: idx[gen] = obj
    return jsonify(idx)

@app.route("/api/preview")
def preview():
    path = request.args.get("path", "")
    if not path:
        return jsonify({"error": "no path provided"})
    host_path = normalize_path_for_host(path)
    if not host_path.startswith(AI_GEN_DIR):
        return jsonify({"error": "file not allowed for preview or not found (path outside allowed dir)"})
    try:
        with open(host_path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read(2000)
            return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": f"could not open file: {str(e)}"})

@app.route("/")
def root():
    return jsonify({"message": "Dashboard running. Visit /dashboard"})

@app.route("/dashboard")
def dashboard():
    return render_template_string(DASHBOARD_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
