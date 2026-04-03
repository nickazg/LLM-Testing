from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

RESULTS_DIR = Path("results")

app = FastAPI(title="LLM Bench Dashboard")


@app.get("/api/results")
async def get_results():
    if not RESULTS_DIR.exists():
        return []
    results = []
    for f in sorted(RESULTS_DIR.glob("*.json")):
        try:
            results.append(json.loads(f.read_text()))
        except json.JSONDecodeError:
            continue
    return results


@app.get("/api/summary")
async def get_summary():
    results = await get_results()
    models = sorted(set(r["model"] for r in results))
    clis = sorted(set(r["cli"] for r in results))
    tasks = sorted(set(r["task_id"] for r in results))
    return {
        "total_runs": len(results),
        "models": models,
        "clis": clis,
        "tasks": tasks,
    }


@app.get("/", response_class=HTMLResponse)
async def index():
    return DASHBOARD_HTML


@app.get("/report", response_class=HTMLResponse)
async def report():
    return REPORT_HTML


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLM Bench</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root { --bg: #0d1117; --surface: #161b22; --border: #30363d; --text: #e6edf3; --muted: #7d8590; --accent: #58a6ff; --green: #3fb950; --yellow: #d29922; --red: #f85149; --purple: #bc8cff; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace; background: var(--bg); color: var(--text); font-size: 13px; }
a { color: var(--accent); text-decoration: none; }

/* Layout */
.header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 12px 20px; display: flex; align-items: center; gap: 20px; }
.header h1 { font-size: 14px; font-weight: 600; }
.header .nav { display: flex; gap: 4px; }
.header .nav button { padding: 5px 12px; border-radius: 4px; border: 1px solid var(--border); background: transparent; color: var(--muted); cursor: pointer; font-size: 12px; }
.header .nav button.active { background: var(--accent); color: #000; border-color: var(--accent); }
.header .report-link { margin-left: auto; font-size: 12px; }
.container { padding: 16px 20px; }

/* Stats bar */
.stats { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 10px 16px; min-width: 100px; }
.stat-val { font-size: 20px; font-weight: 700; color: var(--accent); }
.stat-lbl { font-size: 11px; color: var(--muted); }

/* Filters */
.filters { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; align-items: center; }
.filters label { font-size: 11px; color: var(--muted); margin-right: 2px; }
.filters select { background: var(--surface); color: var(--text); border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; font-size: 12px; }

/* Cards and tables */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-bottom: 12px; }
.card h2 { font-size: 12px; color: var(--muted); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 12px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th { text-align: left; padding: 6px 8px; color: var(--muted); font-weight: 500; border-bottom: 1px solid var(--border); }
td { padding: 6px 8px; border-bottom: 1px solid var(--border); }
tr:hover td { background: rgba(88,166,255,0.05); }
tr.clickable { cursor: pointer; }
.pass { color: var(--green); }
.partial { color: var(--yellow); }
.fail { color: var(--red); }
.mono { font-family: 'SF Mono', Menlo, monospace; font-size: 11px; }
canvas { max-height: 260px; }

/* Detail panel */
.detail-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 16px; margin-bottom: 12px; }
.detail-panel h3 { font-size: 13px; margin-bottom: 10px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.detail-field { }
.detail-field .lbl { font-size: 11px; color: var(--muted); }
.detail-field .val { font-size: 13px; margin-top: 2px; }
.code-block { background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 10px; font-family: 'SF Mono', Menlo, monospace; font-size: 11px; white-space: pre-wrap; word-break: break-word; max-height: 300px; overflow-y: auto; margin-top: 6px; }
.token-bar { display: flex; height: 20px; border-radius: 4px; overflow: hidden; margin-top: 4px; }
.token-bar div { display: flex; align-items: center; justify-content: center; font-size: 10px; color: #000; font-weight: 600; }
.tok-in { background: var(--accent); }
.tok-think { background: var(--purple); }
.tok-out { background: var(--green); }
.tok-cache { background: var(--muted); }

/* Conversation thread */
.conv-thread { margin-top: 12px; }
.conv-msg { border-left: 3px solid var(--border); padding: 8px 12px; margin: 6px 0; border-radius: 0 4px 4px 0; }
.conv-msg.thinking { border-color: var(--purple); background: rgba(188,140,255,0.06); }
.conv-msg.response { border-color: var(--green); background: rgba(63,185,80,0.06); }
.conv-msg.tool_use { border-color: var(--accent); background: rgba(88,166,255,0.06); }
.conv-msg.tool_result { border-color: var(--yellow); background: rgba(210,153,34,0.06); }
.conv-msg.error { border-color: var(--red); background: rgba(248,81,73,0.06); }
.conv-msg-role { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.conv-msg.thinking .conv-msg-role { color: var(--purple); }
.conv-msg.response .conv-msg-role { color: var(--green); }
.conv-msg.tool_use .conv-msg-role { color: var(--accent); }
.conv-msg.tool_result .conv-msg-role { color: var(--yellow); }
.conv-msg.error .conv-msg-role { color: var(--red); }
.conv-msg-content { font-family: 'SF Mono', Menlo, monospace; font-size: 11px; white-space: pre-wrap; word-break: break-word; max-height: 200px; overflow-y: auto; }
.conv-msg-content.collapsed { max-height: 60px; overflow: hidden; cursor: pointer; }
.conv-expand { font-size: 10px; color: var(--accent); cursor: pointer; margin-top: 4px; }
.section-toggle { font-size: 11px; color: var(--accent); cursor: pointer; margin-bottom: 8px; user-select: none; }

/* Split detail layout */
.detail-split { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
.detail-left, .detail-right { min-width: 0; }

/* File explorer */
.file-explorer { background: var(--bg); border: 1px solid var(--border); border-radius: 4px; margin-bottom: 8px; }
.file-explorer-header { font-size: 11px; color: var(--muted); padding: 6px 10px; border-bottom: 1px solid var(--border); text-transform: uppercase; letter-spacing: 0.5px; }
.file-item { padding: 5px 10px; font-size: 12px; font-family: 'SF Mono', Menlo, monospace; cursor: pointer; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid var(--border); }
.file-item:last-child { border-bottom: none; }
.file-item:hover { background: rgba(88,166,255,0.08); }
.file-item.active { background: rgba(88,166,255,0.15); color: var(--accent); }
.file-icon { font-size: 10px; opacity: 0.6; }
.file-lang { font-size: 9px; color: var(--muted); margin-left: auto; }
.file-viewer { background: var(--bg); border: 1px solid var(--border); border-radius: 4px; }
.file-viewer-header { font-size: 11px; color: var(--accent); padding: 6px 10px; border-bottom: 1px solid var(--border); font-family: 'SF Mono', Menlo, monospace; display: flex; justify-content: space-between; }
.file-viewer-content { padding: 10px; font-family: 'SF Mono', Menlo, monospace; font-size: 11px; white-space: pre-wrap; word-break: break-word; max-height: 500px; overflow-y: auto; line-height: 1.5; }
.file-viewer-content .line-num { display: inline-block; width: 35px; color: var(--muted); text-align: right; margin-right: 12px; user-select: none; }
.no-files { color: var(--muted); font-size: 12px; padding: 16px; text-align: center; }

/* Compare */
.compare-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.compare-col { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px; }
.compare-col h3 { font-size: 12px; margin-bottom: 8px; color: var(--accent); }
.delta { font-weight: 700; }
.delta.pos { color: var(--green); }
.delta.neg { color: var(--red); }
.delta.zero { color: var(--muted); }

/* Views */
.view { display: none; }
.view.active { display: block; }
</style>
</head>
<body>

<div class="header">
    <h1>LLM Bench</h1>
    <div class="nav">
        <button class="active" onclick="showView('overview',this)">Overview</button>
        <button onclick="showView('runs',this)">Runs</button>
        <button onclick="showView('compare',this)">Compare</button>
        <button onclick="showView('uplift',this)">Skill Uplift</button>
    </div>
    <a class="report-link" href="/report" target="_blank">Export Report</a>
</div>

<div class="container">
    <div class="stats" id="stats"></div>

    <!-- OVERVIEW -->
    <div id="view-overview" class="view active">
        <div class="grid" id="overview-grid"></div>
    </div>

    <!-- RUNS -->
    <div id="view-runs" class="view">
        <div class="filters" id="run-filters"></div>
        <div id="run-table"></div>
        <div id="run-detail"></div>
    </div>

    <!-- COMPARE -->
    <div id="view-compare" class="view">
        <div class="filters" id="compare-filters"></div>
        <div id="compare-content"></div>
    </div>

    <!-- SKILL UPLIFT -->
    <div id="view-uplift" class="view">
        <div id="uplift-content"></div>
    </div>
</div>

<script>
let R = [];
const C = { accent:'#58a6ff', green:'#3fb950', yellow:'#d29922', red:'#f85149', purple:'#bc8cff', muted:'#7d8590' };

async function init() {
    R = await (await fetch('/api/results')).json();
    renderStats();
    renderOverview();
    renderRunsView();
    renderCompareView();
    renderUpliftView();
}

function showView(name, btn) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById('view-'+name).classList.add('active');
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    if(btn) btn.classList.add('active');
}

function sc(v) { return v>=0.8?'pass':v>=0.5?'partial':'fail'; }
function fmt(v,d) { return v!=null?v.toFixed(d!=null?d:2):'-'; }
function tokTotal(t) { return t?(t.input||0)+(t.output||0)+(t.thinking||0):0; }
function uniq(arr,key) { return [...new Set(arr.map(r=>r[key]))].sort(); }

function renderStats() {
    const m=uniq(R,'model'), c=uniq(R,'cli'), t=uniq(R,'task_id');
    const passed=R.filter(r=>r.scores.correctness>=0.5).length;
    document.getElementById('stats').innerHTML =
        `<div class="stat"><div class="stat-val">${R.length}</div><div class="stat-lbl">Runs</div></div>`+
        `<div class="stat"><div class="stat-val">${m.length}</div><div class="stat-lbl">Models</div></div>`+
        `<div class="stat"><div class="stat-val">${c.length}</div><div class="stat-lbl">CLIs</div></div>`+
        `<div class="stat"><div class="stat-val">${t.length}</div><div class="stat-lbl">Tasks</div></div>`+
        `<div class="stat"><div class="stat-val ${sc(passed/R.length)}">${passed}/${R.length}</div><div class="stat-lbl">Pass Rate</div></div>`;
}

// === OVERVIEW ===
function renderOverview() {
    const models=uniq(R,'model'), clis=uniq(R,'cli');
    let h = '';

    // Matrix
    h += '<div class="card" style="grid-column:1/-1"><h2>Correctness Matrix</h2><table><tr><th>Model</th>';
    clis.forEach(c => h += '<th>'+c+'</th>');
    h += '<th>Avg</th></tr>';
    models.forEach(m => {
        h += '<tr><td><b>'+m+'</b></td>';
        let mAvg=[];
        clis.forEach(c => {
            const runs=R.filter(r=>r.model===m&&r.cli===c);
            if(!runs.length){h+='<td>-</td>';return;}
            const avg=runs.reduce((s,r)=>s+(r.scores.correctness||0),0)/runs.length;
            mAvg.push(avg);
            h += '<td class="'+sc(avg)+'">'+fmt(avg)+'</td>';
        });
        const a=mAvg.length?mAvg.reduce((a,b)=>a+b,0)/mAvg.length:0;
        h += '<td class="'+sc(a)+'"><b>'+fmt(a)+'</b></td></tr>';
    });
    h += '</table></div>';

    // Token efficiency
    h += '<div class="card"><h2>Avg Tokens by Model</h2><canvas id="chart-tokens"></canvas></div>';
    h += '<div class="card"><h2>Avg Time by Model</h2><canvas id="chart-time"></canvas></div>';

    document.getElementById('overview-grid').innerHTML = h;

    // Charts
    const tokData=models.map(m=>{const runs=R.filter(r=>r.model===m&&r.scores.efficiency);return runs.length?runs.reduce((s,r)=>s+tokTotal(r.scores.efficiency.tokens),0)/runs.length:0;});
    const timeData=models.map(m=>{const runs=R.filter(r=>r.model===m&&r.scores.efficiency);return runs.length?runs.reduce((s,r)=>s+(r.scores.efficiency.wall_time_s||0),0)/runs.length:0;});
    const colors=models.map((_,i)=>[C.accent,C.green,C.yellow,C.red,C.purple][i%5]);

    newChart('chart-tokens','bar',models,tokData,colors,'Tokens');
    newChart('chart-time','bar',models,timeData,colors,'Seconds');
}

function newChart(id,type,labels,data,bg,yLabel) {
    const el=document.getElementById(id); if(!el) return;
    new Chart(el,{type,data:{labels,datasets:[{data,backgroundColor:bg}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{color:'#7d8590'},grid:{color:'#30363d'},title:{display:!!yLabel,text:yLabel,color:'#7d8590'}},x:{ticks:{color:'#7d8590'},grid:{color:'#30363d'}}}}});
}

// === RUNS ===
function renderRunsView() {
    const models=uniq(R,'model'), clis=uniq(R,'cli'), tasks=uniq(R,'task_id');
    let f = '<label>Model</label><select id="f-model"><option value="">All</option>';
    models.forEach(m=>f+='<option>'+m+'</option>');
    f += '</select><label>CLI</label><select id="f-cli"><option value="">All</option>';
    clis.forEach(c=>f+='<option>'+c+'</option>');
    f += '</select><label>Task</label><select id="f-task"><option value="">All</option>';
    tasks.forEach(t=>f+='<option>'+t+'</option>');
    f += '</select><label>Result</label><select id="f-result"><option value="">All</option><option>Pass</option><option>Fail</option></select>';
    document.getElementById('run-filters').innerHTML = f;
    ['f-model','f-cli','f-task','f-result'].forEach(id=>document.getElementById(id).onchange=renderRunTable);
    renderRunTable();
}

function renderRunTable() {
    const fm=document.getElementById('f-model').value;
    const fc=document.getElementById('f-cli').value;
    const ft=document.getElementById('f-task').value;
    const fr=document.getElementById('f-result').value;
    let filtered=R.filter(r=>{
        if(fm&&r.model!==fm) return false;
        if(fc&&r.cli!==fc) return false;
        if(ft&&r.task_id!==ft) return false;
        if(fr==='Pass'&&(r.scores.correctness||0)<0.5) return false;
        if(fr==='Fail'&&(r.scores.correctness||0)>=0.5) return false;
        return true;
    });
    let h='<table><tr><th>#</th><th>Task</th><th>Tier</th><th>Model</th><th>CLI</th><th>Correct</th><th>Tokens</th><th>In/Think/Out</th><th>Time</th><th>Cost</th><th>Skill</th></tr>';
    filtered.forEach((r,i) => {
        const e=r.scores.efficiency||{};
        const t=e.tokens||{};
        const total=tokTotal(t);
        const c=r.scores.correctness;
        h += '<tr class="clickable" onclick="showRunDetail('+i+')">';
        h += '<td class="mono">'+(i+1)+'</td>';
        h += '<td>'+r.task_id+'</td>';
        h += '<td>'+(r.tier||'-')+'</td>';
        h += '<td>'+r.model+'</td>';
        h += '<td>'+r.cli+'</td>';
        h += '<td class="'+sc(c||0)+'">'+fmt(c)+'</td>';
        h += '<td class="mono">'+(total||'-')+'</td>';
        h += '<td class="mono">'+(t.input||0)+'/'+(t.thinking||0)+'/'+(t.output||0)+'</td>';
        h += '<td class="mono">'+(e.wall_time_s?fmt(e.wall_time_s,1)+'s':'-')+'</td>';
        h += '<td class="mono">'+(e.cost_usd?'$'+fmt(e.cost_usd,4):'-')+'</td>';
        h += '<td>'+(r.skill||'-')+'</td>';
        h += '</tr>';
    });
    h += '</table>';
    document.getElementById('run-table').innerHTML = '<div class="card"><h2>Runs ('+filtered.length+')</h2>'+h+'</div>';
    document.getElementById('run-detail').innerHTML = '';
    window._filteredRuns = filtered;
}

function showRunDetail(idx) {
    const r = window._filteredRuns[idx];
    if(!r) return;
    const e=r.scores.efficiency||{};
    const t=e.tokens||{};
    const total=tokTotal(t);
    const conv=r.conversation||[];
    const files=r.files||[];

    let h = '<div class="detail-panel">';
    h += '<h3>'+r.task_id+' | '+r.model+' | '+r.cli+'</h3>';

    // Metrics grid
    h += '<div class="detail-grid">';
    h += df('Task ID', r.task_id) + df('Model', r.model) + df('CLI', r.cli);
    h += df('Tier', r.tier||'-') + df('Skill', r.skill||'none') + df('Timestamp', r.timestamp);
    h += df('Correctness', '<span class="'+sc(r.scores.correctness||0)+'">'+fmt(r.scores.correctness)+'</span>');
    h += df('Completion', fmt(r.scores.completion));
    h += df('Wall Time', e.wall_time_s?fmt(e.wall_time_s,1)+'s':'-');
    h += df('Cost', e.cost_usd?'$'+fmt(e.cost_usd,4):'-');
    h += df('Tool Calls', e.tool_calls||0);
    h += df('Total Tokens', total);
    h += '</div>';

    // Token breakdown bar
    if(total) {
        h += '<div class="detail-field"><div class="lbl">Token Breakdown</div>';
        h += '<div class="token-bar">';
        const pIn=((t.input||0)/total*100);
        const pTh=((t.thinking||0)/total*100);
        const pOut=((t.output||0)/total*100);
        if(pIn>2) h+='<div class="tok-in" style="width:'+pIn+'%">IN '+(t.input||0)+'</div>';
        if(pTh>2) h+='<div class="tok-think" style="width:'+pTh+'%">THINK '+(t.thinking||0)+'</div>';
        if(pOut>2) h+='<div class="tok-out" style="width:'+pOut+'%">OUT '+(t.output||0)+'</div>';
        h += '</div>';
        if(t.cache_read) h+='<div style="font-size:11px;color:var(--muted);margin-top:4px;">Cache read: '+t.cache_read+' tokens</div>';
        h += '</div>';
    }

    // === SPLIT LAYOUT: conversation left, files right ===
    h += '<div class="detail-split">';

    // LEFT: Prompt + Conversation
    h += '<div class="detail-left">';

    // Input prompt
    h += '<div class="section-toggle" onclick="toggleSection(\'sec-prompt\')">INPUT PROMPT</div>';
    h += '<div id="sec-prompt" class="code-block" style="max-height:120px">'+esc(r.prompt||'(no prompt)')+'</div>';

    // Conversation
    if(conv.length) {
        h += '<div style="margin-top:12px">';
        h += '<div class="section-toggle" onclick="toggleSection(\'sec-conv\')">CONVERSATION ('+conv.length+' messages)</div>';
        h += '<div id="sec-conv" class="conv-thread">';

        // Render chronologically — each message in order
        conv.forEach(function(m,i) {
            h += '<div class="conv-msg '+m.role+'">';
            var label = m.role.toUpperCase();
            if(m.tool_name) label += ': '+m.tool_name;
            h += '<div class="conv-msg-role">'+label+'</div>';
            h += '<div class="conv-msg-content'+(m.content.length>400?' collapsed':'')+'" id="conv-'+i+'" onclick="toggleExpand(\'conv-'+i+'\')">'+esc(m.content)+'</div>';
            if(m.content.length>400) h += '<div class="conv-expand" onclick="toggleExpand(\'conv-'+i+'\')">click to expand</div>';
            h += '</div>';
        });

        h += '</div></div>';
    } else if(r.raw_output) {
        h += '<div style="margin-top:12px">';
        h += '<div class="section-toggle" onclick="toggleSection(\'sec-raw\')">RAW OUTPUT</div>';
        var parsed = r.raw_output;
        try { parsed = JSON.stringify(JSON.parse(r.raw_output), null, 2); } catch(e) {}
        h += '<div id="sec-raw" class="code-block" style="max-height:400px">'+esc(parsed)+'</div>';
        h += '</div>';
    }

    h += '</div>'; // end detail-left

    // RIGHT: File explorer + viewer
    h += '<div class="detail-right">';

    if(files.length) {
        // File explorer
        h += '<div class="file-explorer">';
        h += '<div class="file-explorer-header">Files Created ('+files.length+')</div>';
        files.forEach(function(f,i) {
            var icon = f.language==='python'?'py':f.language==='javascript'?'js':f.language||'f';
            h += '<div class="file-item'+(i===0?' active':'')+'" onclick="selectFile('+idx+','+i+')" id="fitem-'+i+'">';
            h += '<span class="file-icon">['+icon+']</span>';
            h += '<span>'+esc(f.path)+'</span>';
            if(f.language) h += '<span class="file-lang">'+f.language+'</span>';
            h += '</div>';
        });
        h += '</div>';

        // File viewer — show first file by default
        h += '<div class="file-viewer">';
        h += '<div class="file-viewer-header" id="fviewer-header">'+esc(files[0].path)+'<span class="file-lang">'+(files[0].language||'')+'</span></div>';
        h += '<div class="file-viewer-content" id="fviewer-content">'+addLineNumbers(esc(files[0].content))+'</div>';
        h += '</div>';
    } else {
        h += '<div class="no-files">No files were created by the model in this run.</div>';
    }

    h += '</div>'; // end detail-right
    h += '</div>'; // end detail-split

    h += '</div>'; // end detail-panel
    document.getElementById('run-detail').innerHTML = h;
    document.getElementById('run-detail').scrollIntoView({behavior:'smooth'});

    // Store files for selection
    window._detailFiles = files;
}

function selectFile(runIdx, fileIdx) {
    const files = window._detailFiles || [];
    const f = files[fileIdx];
    if(!f) return;

    // Update active state
    document.querySelectorAll('.file-item').forEach(function(el,i) {
        el.classList.toggle('active', i===fileIdx);
    });

    // Update viewer
    document.getElementById('fviewer-header').innerHTML = esc(f.path)+'<span class="file-lang">'+(f.language||'')+'</span>';
    document.getElementById('fviewer-content').innerHTML = addLineNumbers(esc(f.content));
}

function addLineNumbers(text) {
    return text.split('\n').map(function(line, i) {
        return '<span class="line-num">'+(i+1)+'</span>'+line;
    }).join('\n');
}

function toggleSection(id) {
    const el = document.getElementById(id);
    if(el) el.style.display = el.style.display==='none'?'':'none';
}

function toggleExpand(id) {
    const el = document.getElementById(id);
    if(el) el.classList.toggle('collapsed');
}

function df(lbl,val) { return '<div class="detail-field"><div class="lbl">'+lbl+'</div><div class="val">'+val+'</div></div>'; }
function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// === COMPARE ===
function renderCompareView() {
    const models=uniq(R,'model'), clis=uniq(R,'cli');
    let f = '<label>Compare</label><select id="cmp-type"><option value="model">Models</option><option value="cli">CLIs</option></select>';
    f += '<label>A</label><select id="cmp-a"></select>';
    f += '<label>B</label><select id="cmp-b"></select>';
    document.getElementById('compare-filters').innerHTML = f;
    document.getElementById('cmp-type').onchange = updateCompareOptions;
    document.getElementById('cmp-a').onchange = renderComparison;
    document.getElementById('cmp-b').onchange = renderComparison;
    updateCompareOptions();
}

function updateCompareOptions() {
    const type = document.getElementById('cmp-type').value;
    const opts = type==='model' ? uniq(R,'model') : uniq(R,'cli');
    const selA = document.getElementById('cmp-a');
    const selB = document.getElementById('cmp-b');
    selA.innerHTML = opts.map(o=>'<option>'+o+'</option>').join('');
    selB.innerHTML = opts.map(o=>'<option>'+o+'</option>').join('');
    if(opts.length>1) selB.selectedIndex=1;
    renderComparison();
}

function renderComparison() {
    const type = document.getElementById('cmp-type').value;
    const a = document.getElementById('cmp-a').value;
    const b = document.getElementById('cmp-b').value;
    const key = type==='model'?'model':'cli';

    const runsA = R.filter(r=>r[key]===a);
    const runsB = R.filter(r=>r[key]===b);

    function avg(runs, fn) { if(!runs.length)return 0; return runs.reduce((s,r)=>s+fn(r),0)/runs.length; }

    const metrics = [
        {name:'Correctness', fn:r=>r.scores.correctness||0},
        {name:'Completion', fn:r=>r.scores.completion||0},
        {name:'Total Tokens', fn:r=>tokTotal((r.scores.efficiency||{}).tokens||{}), lower:true},
        {name:'Input Tokens', fn:r=>((r.scores.efficiency||{}).tokens||{}).input||0, lower:true},
        {name:'Thinking Tokens', fn:r=>((r.scores.efficiency||{}).tokens||{}).thinking||0, lower:true},
        {name:'Output Tokens', fn:r=>((r.scores.efficiency||{}).tokens||{}).output||0, lower:true},
        {name:'Wall Time (s)', fn:r=>(r.scores.efficiency||{}).wall_time_s||0, lower:true},
        {name:'Tool Calls', fn:r=>(r.scores.efficiency||{}).tool_calls||0, lower:true},
        {name:'Cost ($)', fn:r=>(r.scores.efficiency||{}).cost_usd||0, lower:true},
    ];

    let h = '<div class="card"><h2>'+a+' vs '+b+'</h2>';
    h += '<table><tr><th>Metric</th><th>'+a+'</th><th>'+b+'</th><th>Delta</th></tr>';
    metrics.forEach(m => {
        const va=avg(runsA,m.fn), vb=avg(runsB,m.fn);
        const d=va-vb;
        const isP = m.lower ? d<0 : d>0;
        const cls = Math.abs(d)<0.001?'zero':isP?'pos':'neg';
        const sign = d>0?'+':'';
        h += '<tr><td>'+m.name+'</td><td class="mono">'+fmt(va,2)+'</td><td class="mono">'+fmt(vb,2)+'</td><td class="mono delta '+cls+'">'+sign+fmt(d,2)+'</td></tr>';
    });
    h += '</table></div>';

    // Per-task breakdown
    const tasks = uniq(R,'task_id');
    h += '<div class="card"><h2>Per-Task Correctness</h2><table><tr><th>Task</th><th>'+a+'</th><th>'+b+'</th><th>Delta</th></tr>';
    tasks.forEach(t => {
        const ra=R.filter(r=>r[key]===a&&r.task_id===t);
        const rb=R.filter(r=>r[key]===b&&r.task_id===t);
        const va=ra.length?avg(ra,r=>r.scores.correctness||0):null;
        const vb=rb.length?avg(rb,r=>r.scores.correctness||0):null;
        if(va===null&&vb===null)return;
        const d=(va||0)-(vb||0);
        const cls=Math.abs(d)<0.001?'zero':d>0?'pos':'neg';
        h += '<tr><td>'+t+'</td><td class="mono '+(va!=null?sc(va):'')+'">'+(va!=null?fmt(va):'-')+'</td><td class="mono '+(vb!=null?sc(vb):'')+'">'+(vb!=null?fmt(vb):'-')+'</td><td class="mono delta '+cls+'">'+(d>0?'+':'')+fmt(d)+'</td></tr>';
    });
    h += '</table></div>';

    document.getElementById('compare-content').innerHTML = h;
}

// === SKILL UPLIFT ===
function renderUpliftView() {
    const tier3=R.filter(r=>(r.tier||0)===3);
    const tier4=R.filter(r=>(r.tier||0)===4);
    const models=uniq(R,'model');

    if(!tier3.length && !tier4.length) {
        document.getElementById('uplift-content').innerHTML = '<div class="card"><h2>Skill Uplift</h2><p style="color:var(--muted)">No tier 3/4 results yet. Run domain-specific tasks with and without skills to see uplift data.</p></div>';
        return;
    }

    let h = '<div class="card"><h2>Skill Uplift — Correctness Delta (Tier 4 - Tier 3)</h2>';
    h += '<canvas id="uplift-chart" style="max-height:300px"></canvas></div>';

    // Table
    h += '<div class="card"><h2>Skill Uplift Detail</h2>';
    h += '<table><tr><th>Model</th><th>Tier 3 (no skill)</th><th>Tier 4 (with skill)</th><th>Uplift</th><th>Interpretation</th></tr>';
    const t3s=[],t4s=[];
    models.forEach(m => {
        const r3=tier3.filter(r=>r.model===m);
        const r4=tier4.filter(r=>r.model===m);
        const v3=r3.length?r3.reduce((s,r)=>s+(r.scores.correctness||0),0)/r3.length:null;
        const v4=r4.length?r4.reduce((s,r)=>s+(r.scores.correctness||0),0)/r4.length:null;
        t3s.push(v3||0); t4s.push(v4||0);
        if(v3===null&&v4===null)return;
        const d=(v4||0)-(v3||0);
        const cls=Math.abs(d)<0.01?'zero':d>0?'pos':'neg';
        let interp='-';
        if(v3!==null&&v4!==null){
            if(d>0.3) interp='<span class="pass">Strong uplift — skill significantly helps</span>';
            else if(d>0.1) interp='<span class="partial">Moderate uplift</span>';
            else if(d>-0.05) interp='<span style="color:var(--muted)">Minimal effect</span>';
            else interp='<span class="fail">Negative — skill may confuse model</span>';
        }
        h += '<tr><td><b>'+m+'</b></td>';
        h += '<td class="mono '+(v3!=null?sc(v3):'')+'">'+(v3!=null?fmt(v3):'-')+'</td>';
        h += '<td class="mono '+(v4!=null?sc(v4):'')+'">'+(v4!=null?fmt(v4):'-')+'</td>';
        h += '<td class="mono delta '+cls+'">'+(d>0?'+':'')+fmt(d)+'</td>';
        h += '<td>'+interp+'</td></tr>';
    });
    h += '</table></div>';

    document.getElementById('uplift-content').innerHTML = h;

    new Chart(document.getElementById('uplift-chart'),{
        type:'bar',
        data:{labels:models,datasets:[
            {label:'Tier 3 (no skill)',data:t3s,backgroundColor:C.red},
            {label:'Tier 4 (with skill)',data:t4s,backgroundColor:C.green},
        ]},
        options:{responsive:true,scales:{y:{min:0,max:1,ticks:{color:'#7d8590'},grid:{color:'#30363d'}},x:{ticks:{color:'#7d8590'},grid:{color:'#30363d'}}},plugins:{legend:{labels:{color:'#e6edf3'}}}}
    });
}

init();
</script>
</body>
</html>"""


REPORT_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLM Bench Report</title>
<style>
@media print { body { font-size: 11px; } .no-print { display: none !important; } }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 20px; color: #1f2937; background: #fff; line-height: 1.5; }
h1 { font-size: 22px; margin-bottom: 4px; }
h2 { font-size: 16px; margin: 24px 0 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }
h3 { font-size: 13px; margin: 16px 0 6px; color: #6b7280; }
.subtitle { color: #6b7280; font-size: 13px; margin-bottom: 24px; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 16px; font-size: 12px; }
th { text-align: left; padding: 6px 8px; background: #f9fafb; border: 1px solid #e5e7eb; font-weight: 600; }
td { padding: 6px 8px; border: 1px solid #e5e7eb; }
.pass { color: #059669; font-weight: 600; }
.partial { color: #d97706; font-weight: 600; }
.fail { color: #dc2626; font-weight: 600; }
.mono { font-family: 'SF Mono', Menlo, monospace; font-size: 11px; }
.metric-bar { display:inline-block; height:12px; border-radius:2px; margin-right:4px; }
.summary-box { background: #f3f4f6; border-radius: 6px; padding: 12px 16px; margin: 12px 0; }
.btn { display:inline-block; padding:8px 16px; background:#2563eb; color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:12px; margin: 8px 4px 8px 0; }
.btn:hover { background:#1d4ed8; }
.finding { padding: 8px 12px; margin: 4px 0; border-left: 3px solid #2563eb; background: #eff6ff; font-size: 12px; }
</style>
</head>
<body>

<div class="no-print" style="margin-bottom:16px;">
    <button class="btn" onclick="window.print()">Print / Save PDF</button>
    <button class="btn" onclick="copyMarkdown()" style="background:#059669">Copy as Markdown</button>
    <a class="btn" href="/" style="background:#6b7280;text-decoration:none;">Back to Dashboard</a>
</div>

<h1>LLM Bench — Benchmark Report</h1>
<div class="subtitle" id="report-subtitle"></div>

<div id="report-body">Loading...</div>

<script>
let R = [];

async function init() {
    R = await (await fetch('/api/results')).json();
    render();
}

function sc(v) { return v>=0.8?'pass':v>=0.5?'partial':'fail'; }
function fmt(v,d) { return v!=null?v.toFixed(d!=null?d:2):'-'; }
function tokTotal(t) { return t?(t.input||0)+(t.output||0)+(t.thinking||0):0; }
function uniq(arr,key) { return [...new Set(arr.map(r=>r[key]))].sort(); }

function render() {
    const models=uniq(R,'model'), clis=uniq(R,'cli'), tasks=uniq(R,'task_id');
    const passed=R.filter(r=>(r.scores.correctness||0)>=0.5).length;
    const now=new Date().toISOString().slice(0,10);

    document.getElementById('report-subtitle').textContent = 'Generated '+now+' — '+R.length+' runs across '+models.length+' models, '+clis.length+' CLIs, '+tasks.length+' tasks';

    let h = '';

    // Executive summary
    h += '<h2>Executive Summary</h2>';
    h += '<div class="summary-box">';
    h += '<b>'+R.length+'</b> benchmark runs completed. ';
    h += '<b>'+passed+'</b> passed ('+fmt(passed/R.length*100,0)+'%). ';
    h += 'Models tested: <b>'+models.join(', ')+'</b>. ';
    h += 'CLI interfaces: <b>'+clis.join(', ')+'</b>.';
    h += '</div>';

    // Key findings
    h += '<h2>Key Findings</h2>';
    const modelAvgs=models.map(m=>{const runs=R.filter(r=>r.model===m);return{model:m,correctness:runs.reduce((s,r)=>s+(r.scores.correctness||0),0)/runs.length,tokens:runs.reduce((s,r)=>s+tokTotal((r.scores.efficiency||{}).tokens||{}),0)/runs.length,time:runs.reduce((s,r)=>s+((r.scores.efficiency||{}).wall_time_s||0),0)/runs.length};});
    modelAvgs.sort((a,b)=>b.correctness-a.correctness);
    if(modelAvgs.length) {
        h += '<div class="finding">Best correctness: <b>'+modelAvgs[0].model+'</b> ('+fmt(modelAvgs[0].correctness)+')</div>';
        const fastest=modelAvgs.filter(m=>m.time>0).sort((a,b)=>a.time-b.time);
        if(fastest.length) h += '<div class="finding">Fastest: <b>'+fastest[0].model+'</b> ('+fmt(fastest[0].time,1)+'s avg)</div>';
        const cheapest=modelAvgs.filter(m=>m.tokens>0).sort((a,b)=>a.tokens-b.tokens);
        if(cheapest.length) h += '<div class="finding">Most token-efficient: <b>'+cheapest[0].model+'</b> ('+Math.round(cheapest[0].tokens)+' avg tokens)</div>';
    }

    // Skill uplift findings
    const t3=R.filter(r=>(r.tier||0)===3), t4=R.filter(r=>(r.tier||0)===4);
    if(t3.length&&t4.length) {
        models.forEach(m=>{
            const r3=t3.filter(r=>r.model===m), r4=t4.filter(r=>r.model===m);
            if(!r3.length||!r4.length)return;
            const v3=r3.reduce((s,r)=>s+(r.scores.correctness||0),0)/r3.length;
            const v4=r4.reduce((s,r)=>s+(r.scores.correctness||0),0)/r4.length;
            const d=v4-v3;
            if(Math.abs(d)>0.05) h+='<div class="finding">Skill uplift for <b>'+m+'</b>: '+(d>0?'+':'')+fmt(d)+' ('+(d>0?'improvement':'regression')+')</div>';
        });
    }

    // Correctness matrix
    h += '<h2>Correctness Matrix</h2>';
    h += '<table><tr><th>Model</th>';
    clis.forEach(c=>h+='<th>'+c+'</th>');
    h += '<th>Average</th></tr>';
    models.forEach(m=>{
        h+='<tr><td><b>'+m+'</b></td>';
        let vals=[];
        clis.forEach(c=>{
            const runs=R.filter(r=>r.model===m&&r.cli===c);
            if(!runs.length){h+='<td>-</td>';return;}
            const avg=runs.reduce((s,r)=>s+(r.scores.correctness||0),0)/runs.length;
            vals.push(avg);
            h+='<td class="'+sc(avg)+'">'+fmt(avg)+'</td>';
        });
        const a=vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:0;
        h+='<td class="'+sc(a)+'"><b>'+fmt(a)+'</b></td></tr>';
    });
    h += '</table>';

    // Detailed metrics
    h += '<h2>Detailed Metrics by Model</h2>';
    h += '<table><tr><th>Model</th><th>Correctness</th><th>Tokens (avg)</th><th>In/Think/Out</th><th>Time (avg)</th><th>Cost (avg)</th><th>Runs</th></tr>';
    models.forEach(m=>{
        const runs=R.filter(r=>r.model===m);
        const avg_c=runs.reduce((s,r)=>s+(r.scores.correctness||0),0)/runs.length;
        const avg_tok=runs.reduce((s,r)=>s+tokTotal((r.scores.efficiency||{}).tokens||{}),0)/runs.length;
        const avg_in=runs.reduce((s,r)=>s+(((r.scores.efficiency||{}).tokens||{}).input||0),0)/runs.length;
        const avg_th=runs.reduce((s,r)=>s+(((r.scores.efficiency||{}).tokens||{}).thinking||0),0)/runs.length;
        const avg_out=runs.reduce((s,r)=>s+(((r.scores.efficiency||{}).tokens||{}).output||0),0)/runs.length;
        const avg_t=runs.reduce((s,r)=>s+((r.scores.efficiency||{}).wall_time_s||0),0)/runs.length;
        const avg_cost=runs.reduce((s,r)=>s+((r.scores.efficiency||{}).cost_usd||0),0)/runs.length;
        h+='<tr><td><b>'+m+'</b></td>';
        h+='<td class="'+sc(avg_c)+'">'+fmt(avg_c)+'</td>';
        h+='<td class="mono">'+Math.round(avg_tok)+'</td>';
        h+='<td class="mono">'+Math.round(avg_in)+'/'+Math.round(avg_th)+'/'+Math.round(avg_out)+'</td>';
        h+='<td class="mono">'+fmt(avg_t,1)+'s</td>';
        h+='<td class="mono">'+(avg_cost?'$'+fmt(avg_cost,4):'-')+'</td>';
        h+='<td>'+runs.length+'</td></tr>';
    });
    h += '</table>';

    // Skill uplift table
    if(t3.length||t4.length) {
        h += '<h2>Skill Uplift Analysis</h2>';
        h += '<table><tr><th>Model</th><th>Without Skill (T3)</th><th>With Skill (T4)</th><th>Uplift</th></tr>';
        models.forEach(m=>{
            const r3=t3.filter(r=>r.model===m), r4=t4.filter(r=>r.model===m);
            const v3=r3.length?r3.reduce((s,r)=>s+(r.scores.correctness||0),0)/r3.length:null;
            const v4=r4.length?r4.reduce((s,r)=>s+(r.scores.correctness||0),0)/r4.length:null;
            if(v3===null&&v4===null) return;
            const d=(v4||0)-(v3||0);
            h+='<tr><td><b>'+m+'</b></td>';
            h+='<td class="mono">'+(v3!=null?fmt(v3):'-')+'</td>';
            h+='<td class="mono">'+(v4!=null?fmt(v4):'-')+'</td>';
            h+='<td class="mono" style="color:'+(d>0.05?'#059669':d<-0.05?'#dc2626':'#6b7280')+'">'+(d>0?'+':'')+fmt(d)+'</td></tr>';
        });
        h += '</table>';
    }

    // All runs
    h += '<h2>All Runs</h2>';
    h += '<table><tr><th>#</th><th>Task</th><th>Model</th><th>CLI</th><th>Correct</th><th>Tokens</th><th>Time</th><th>Skill</th></tr>';
    R.forEach((r,i) => {
        const e=r.scores.efficiency||{};
        const c=r.scores.correctness;
        h+='<tr><td>'+(i+1)+'</td><td>'+r.task_id+'</td><td>'+r.model+'</td><td>'+r.cli+'</td>';
        h+='<td class="'+sc(c||0)+'">'+fmt(c)+'</td>';
        h+='<td class="mono">'+tokTotal((e.tokens||{}))+'</td>';
        h+='<td class="mono">'+(e.wall_time_s?fmt(e.wall_time_s,1)+'s':'-')+'</td>';
        h+='<td>'+(r.skill||'-')+'</td></tr>';
    });
    h += '</table>';

    document.getElementById('report-body').innerHTML = h;
}

function copyMarkdown() {
    const models=uniq(R,'model'), clis=uniq(R,'cli');
    let md = '# LLM Bench Report\n\n';
    md += 'Generated: '+new Date().toISOString().slice(0,10)+'\n';
    md += R.length+' runs, '+models.length+' models, '+clis.length+' CLIs\n\n';
    md += '## Correctness Matrix\n\n';
    md += '| Model | '+clis.join(' | ')+' |\n';
    md += '|---|'+clis.map(()=>'---').join('|')+'|\n';
    models.forEach(m=>{
        md += '| '+m+' | ';
        clis.forEach(c=>{
            const runs=R.filter(r=>r.model===m&&r.cli===c);
            md += (runs.length?fmt(runs.reduce((s,r)=>s+(r.scores.correctness||0),0)/runs.length):'-')+' | ';
        });
        md += '\n';
    });
    md += '\n## Metrics\n\n| Model | Correctness | Tokens | Time |\n|---|---|---|---|\n';
    models.forEach(m=>{
        const runs=R.filter(r=>r.model===m);
        md += '| '+m+' | '+fmt(runs.reduce((s,r)=>s+(r.scores.correctness||0),0)/runs.length);
        md += ' | '+Math.round(runs.reduce((s,r)=>s+tokTotal((r.scores.efficiency||{}).tokens||{}),0)/runs.length);
        md += ' | '+fmt(runs.reduce((s,r)=>s+((r.scores.efficiency||{}).wall_time_s||0),0)/runs.length,1)+'s |\n';
    });
    navigator.clipboard.writeText(md).then(()=>alert('Markdown copied to clipboard'));
}

init();
</script>
</body>
</html>"""
