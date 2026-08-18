"""Assertion report - one row per validation, grouped by test.

pytest-html reports which *test* failed. This report answers the question a
stakeholder actually asks: which *validation* ran, what was expected, what was
found, and where.
"""

from __future__ import annotations

import html
from collections import OrderedDict
from datetime import datetime

from config.settings import REPORTS_DIR
from utils.verification import SESSION_RESULTS, VerificationResult

_CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", system-ui, sans-serif; margin: 0; padding: 28px;
       background: #f6f7f9; color: #14181f; }
h1 { margin: 0 0 4px; font-size: 22px; }
.sub { color: #6b7280; font-size: 13px; margin-bottom: 22px; }
.cards { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 26px; }
.card { background: #fff; border: 1px solid #e3e6ea; border-radius: 10px;
        padding: 14px 20px; min-width: 132px; }
.card .n { font-size: 26px; font-weight: 650; }
.card .l { font-size: 12px; color: #6b7280; text-transform: uppercase;
           letter-spacing: .5px; }
.pass .n { color: #17803d; } .fail .n { color: #c0261f; }
h2 { font-size: 15px; margin: 26px 0 8px; }
h2 .meta { font-weight: 400; color: #6b7280; font-size: 12.5px; }
.wrap { overflow-x: auto; background: #fff; border: 1px solid #e3e6ea;
        border-radius: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th { text-align: left; background: #f0f2f5; padding: 9px 12px;
     border-bottom: 1px solid #e3e6ea; font-weight: 600; white-space: nowrap; }
td { padding: 9px 12px; border-bottom: 1px solid #eef0f3; vertical-align: top; }
tr:last-child td { border-bottom: none; }
.badge { font-size: 11px; font-weight: 650; padding: 2px 9px; border-radius: 999px;
         letter-spacing: .4px; }
.badge.PASSED { background: #dcfce7; color: #14612f; }
.badge.FAILED { background: #fee2e2; color: #a3170f; }
tr.FAILED { background: #fff7f7; }
code { font-family: ui-monospace, Consolas, monospace; font-size: 12px;
       background: #f2f4f7; padding: 1px 5px; border-radius: 4px; }
a { color: #1d4ed8; }
@media (prefers-color-scheme: dark) {
  body { background: #14181f; color: #e6e9ee; }
  .card, .wrap { background: #1c222b; border-color: #2c333d; }
  th { background: #222933; border-color: #2c333d; }
  td { border-color: #262d37; }
  code { background: #262d37; }
  tr.FAILED { background: #2a1e1e; }
  .sub, .card .l, h2 .meta { color: #9aa4b2; }
}
"""


def _row(index: int, r: VerificationResult) -> str:
    shot = (
        f'<a href="{html.escape(r.screenshot)}">screenshot</a>'
        if r.screenshot
        else ""
    )
    return (
        f'<tr class="{r.status.value}">'
        f"<td>{index}</td>"
        f"<td>{html.escape(r.description)}</td>"
        f"<td><code>{html.escape(r.expected)}</code></td>"
        f"<td><code>{html.escape(r.actual)}</code></td>"
        f'<td><span class="badge {r.status.value}">{r.status.value}</span></td>'
        f"<td>{r.duration_ms} ms</td>"
        f"<td>{r.timestamp}</td>"
        f"<td>{shot}</td>"
        "</tr>"
    )


def write_assertion_report(results: list[VerificationResult] | None = None) -> str:
    """Render the report and return its path. Safe to call with no results."""
    results = SESSION_RESULTS if results is None else results
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target = REPORTS_DIR / "assertion_report.html"

    total = len(results)
    failed = sum(1 for r in results if not r.passed)
    passed = total - failed

    grouped: "OrderedDict[str, list[VerificationResult]]" = OrderedDict()
    for r in results:
        grouped.setdefault(r.test_name or "(unassigned)", []).append(r)

    sections = []
    for test_name, items in grouped.items():
        fails = sum(1 for r in items if not r.passed)
        meta = f"{len(items)} validations, {fails} failed" if fails else f"{len(items)} validations, all passed"
        rows = "".join(_row(i, r) for i, r in enumerate(items, 1))
        sections.append(
            f"<h2>{html.escape(test_name)} <span class='meta'>&mdash; {meta}</span></h2>"
            '<div class="wrap"><table>'
            "<thead><tr><th>#</th><th>Validation</th><th>Expected</th><th>Actual</th>"
            "<th>Result</th><th>Time</th><th>At</th><th>Evidence</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )

    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>inride - Assertion Report</title><style>{_CSS}</style></head>
<body>
<h1>inride &mdash; Assertion Report</h1>
<div class="sub">Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
<div class="cards">
  <div class="card"><div class="n">{total}</div><div class="l">Validations</div></div>
  <div class="card pass"><div class="n">{passed}</div><div class="l">Passed</div></div>
  <div class="card fail"><div class="n">{failed}</div><div class="l">Failed</div></div>
  <div class="card"><div class="n">{len(grouped)}</div><div class="l">Tests</div></div>
</div>
{"".join(sections) or "<p>No validations were recorded.</p>"}
</body></html>"""

    target.write_text(document, encoding="utf-8")
    return str(target)
