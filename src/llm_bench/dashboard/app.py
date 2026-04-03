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


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Bench Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; padding: 24px; }
        h1 { font-size: 1.5rem; margin-bottom: 8px; }
        .subtitle { color: #888; margin-bottom: 24px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 20px; margin-bottom: 24px; }
        .card { background: #1a1d27; border-radius: 8px; padding: 20px; border: 1px solid #2a2d37; }
        .card h2 { font-size: 1rem; margin-bottom: 12px; color: #aaa; }
        .stats { display: flex; gap: 24px; margin-bottom: 24px; flex-wrap: wrap; }
        .stat { background: #1a1d27; border-radius: 8px; padding: 16px 24px; border: 1px solid #2a2d37; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #6c9eff; }
        .stat-label { color: #888; font-size: 0.85rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #2a2d37; }
        th { color: #888; font-weight: 500; }
        .score-high { color: #4ade80; }
        .score-mid { color: #facc15; }
        .score-low { color: #f87171; }
        canvas { max-height: 300px; }
        .tabs { display: flex; gap: 8px; margin-bottom: 16px; }
        .tab { padding: 6px 16px; border-radius: 6px; cursor: pointer; background: #2a2d37; border: none; color: #e0e0e0; font-size: 0.9rem; }
        .tab.active { background: #6c9eff; color: #000; }
    </style>
</head>
<body>
    <h1>LLM Bench Dashboard</h1>
    <p class="subtitle">Model performance across CLI interfaces</p>

    <div class="stats" id="stats"></div>

    <div class="tabs">
        <button class="tab active" onclick="showView('matrix', this)">Matrix</button>
        <button class="tab" onclick="showView('uplift', this)">Skill Uplift</button>
        <button class="tab" onclick="showView('efficiency', this)">Efficiency</button>
        <button class="tab" onclick="showView('runs', this)">Run History</button>
    </div>

    <div id="view-matrix" class="grid"></div>
    <div id="view-uplift" class="grid" style="display:none"></div>
    <div id="view-efficiency" class="grid" style="display:none"></div>
    <div id="view-runs" style="display:none"></div>

<script>
let allResults = [];

async function init() {
    const res = await fetch('/api/results');
    allResults = await res.json();
    renderStats();
    renderMatrix();
    renderUplift();
    renderEfficiency();
    renderRuns();
}

function scoreClass(s) {
    if (s === null || s === undefined) return '';
    if (s >= 0.8) return 'score-high';
    if (s >= 0.5) return 'score-mid';
    return 'score-low';
}

function renderStats() {
    const models = new Set(allResults.map(r => r.model));
    const clis = new Set(allResults.map(r => r.cli));
    const tasks = new Set(allResults.map(r => r.task_id));
    document.getElementById('stats').innerHTML =
        '<div class="stat"><div class="stat-value">' + allResults.length + '</div><div class="stat-label">Total Runs</div></div>' +
        '<div class="stat"><div class="stat-value">' + models.size + '</div><div class="stat-label">Models</div></div>' +
        '<div class="stat"><div class="stat-value">' + clis.size + '</div><div class="stat-label">CLIs</div></div>' +
        '<div class="stat"><div class="stat-value">' + tasks.size + '</div><div class="stat-label">Tasks</div></div>';
}

function renderMatrix() {
    const models = [...new Set(allResults.map(r => r.model))];
    const clis = [...new Set(allResults.map(r => r.cli))];

    let html = '<div class="card" style="grid-column: 1/-1"><h2>Model x CLI - Average Correctness</h2><table><tr><th>Model</th>';
    clis.forEach(function(c) { html += '<th>' + c + '</th>'; });
    html += '</tr>';

    models.forEach(function(model) {
        html += '<tr><td>' + model + '</td>';
        clis.forEach(function(cli) {
            const runs = allResults.filter(function(r) { return r.model === model && r.cli === cli; });
            if (runs.length === 0) {
                html += '<td>-</td>';
            } else {
                const avg = runs.reduce(function(s, r) { return s + (r.scores.correctness || 0); }, 0) / runs.length;
                html += '<td class="' + scoreClass(avg) + '">' + avg.toFixed(2) + '</td>';
            }
        });
        html += '</tr>';
    });

    html += '</table></div>';
    document.getElementById('view-matrix').innerHTML = html;
}

function renderUplift() {
    const tier3 = allResults.filter(function(r) { return r.task_id.startsWith('tier3'); });
    const tier4 = allResults.filter(function(r) { return r.task_id.startsWith('tier4'); });
    const models = [...new Set(allResults.map(function(r) { return r.model; }))];

    if (tier3.length === 0 && tier4.length === 0) {
        document.getElementById('view-uplift').innerHTML = '<div class="card"><h2>Skill Uplift</h2><p>No tier 3/4 results yet. Run domain-specific tasks to see skill uplift data.</p></div>';
        return;
    }

    const t3scores = models.map(function(m) {
        const runs = tier3.filter(function(r) { return r.model === m; });
        return runs.length ? runs.reduce(function(s, r) { return s + (r.scores.correctness || 0); }, 0) / runs.length : 0;
    });
    const t4scores = models.map(function(m) {
        const runs = tier4.filter(function(r) { return r.model === m; });
        return runs.length ? runs.reduce(function(s, r) { return s + (r.scores.correctness || 0); }, 0) / runs.length : 0;
    });

    document.getElementById('view-uplift').innerHTML = '<div class="card" style="grid-column:1/-1"><h2>Skill Uplift - Tier 3 vs Tier 4 Correctness</h2><canvas id="upliftChart"></canvas></div>';

    new Chart(document.getElementById('upliftChart'), {
        type: 'bar',
        data: {
            labels: models,
            datasets: [
                { label: 'Tier 3 (no skill)', data: t3scores, backgroundColor: '#f87171' },
                { label: 'Tier 4 (with skill)', data: t4scores, backgroundColor: '#4ade80' }
            ]
        },
        options: {
            responsive: true,
            scales: { y: { min: 0, max: 1, ticks: { color: '#888' }, grid: { color: '#2a2d37' } }, x: { ticks: { color: '#888' }, grid: { color: '#2a2d37' } } },
            plugins: { legend: { labels: { color: '#e0e0e0' } } }
        }
    });
}

function renderEfficiency() {
    const data = allResults
        .filter(function(r) { return r.scores.efficiency; })
        .map(function(r) {
            return {
                x: r.scores.efficiency.tokens,
                y: r.scores.correctness || 0,
                model: r.model
            };
        });

    const models = [...new Set(data.map(function(d) { return d.model; }))];
    const colors = ['#6c9eff', '#4ade80', '#facc15', '#f87171', '#c084fc'];

    document.getElementById('view-efficiency').innerHTML = '<div class="card" style="grid-column:1/-1"><h2>Efficiency - Tokens vs Correctness</h2><canvas id="effChart"></canvas></div>';

    new Chart(document.getElementById('effChart'), {
        type: 'scatter',
        data: {
            datasets: models.map(function(m, i) {
                return {
                    label: m,
                    data: data.filter(function(d) { return d.model === m; }),
                    backgroundColor: colors[i % colors.length],
                    pointRadius: 6
                };
            })
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Tokens', color: '#888' }, ticks: { color: '#888' }, grid: { color: '#2a2d37' } },
                y: { title: { display: true, text: 'Correctness', color: '#888' }, min: 0, max: 1, ticks: { color: '#888' }, grid: { color: '#2a2d37' } }
            },
            plugins: { legend: { labels: { color: '#e0e0e0' } } }
        }
    });
}

function renderRuns() {
    let html = '<div class="card"><h2>Run History</h2><table><tr><th>Task</th><th>Model</th><th>CLI</th><th>Correct</th><th>Complete</th><th>Tokens</th><th>Time</th><th>Skill</th></tr>';
    allResults.forEach(function(r) {
        const eff = r.scores.efficiency || {};
        html += '<tr>' +
            '<td>' + r.task_id + '</td>' +
            '<td>' + r.model + '</td>' +
            '<td>' + r.cli + '</td>' +
            '<td class="' + scoreClass(r.scores.correctness) + '">' + (r.scores.correctness !== null ? r.scores.correctness.toFixed(2) : '-') + '</td>' +
            '<td class="' + scoreClass(r.scores.completion) + '">' + (r.scores.completion !== null ? r.scores.completion.toFixed(2) : '-') + '</td>' +
            '<td>' + (eff.tokens || '-') + '</td>' +
            '<td>' + (eff.wall_time_s ? eff.wall_time_s.toFixed(1) + 's' : '-') + '</td>' +
            '<td>' + (r.skill || '-') + '</td>' +
            '</tr>';
    });
    html += '</table></div>';
    document.getElementById('view-runs').innerHTML = html;
}

function showView(name, btn) {
    ['matrix', 'uplift', 'efficiency', 'runs'].forEach(function(v) {
        document.getElementById('view-' + v).style.display = v === name ? '' : 'none';
    });
    document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
    btn.classList.add('active');
}

init();
</script>
</body>
</html>"""
