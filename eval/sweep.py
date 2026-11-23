"""Sweep the auto-create confidence threshold to show the core trade-off.

Raising the threshold issues fewer POs automatically but makes the auto-issued
set safer (higher precision). This is the single most important operating dial,
so we plot it explicitly. Run:  python -m eval.sweep
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from po_creation.config import DEFAULT_CONFIG

from eval.harness import evaluate

THRESHOLDS = [0.80, 0.85, 0.90, 0.93, 0.95, 0.98]
SWEEP_JSON = Path("eval/sweep.json")


def run_sweep(thresholds=THRESHOLDS) -> list[dict]:
    rows = []
    for t in thresholds:
        cfg = dataclasses.replace(DEFAULT_CONFIG, auto_create_threshold=t)
        r = evaluate(config=cfg)
        rows.append(
            {
                "threshold": t,
                "auto_create_rate": round(r.auto_create_rate, 4),
                "auto_create_precision": round(r.auto_create_precision, 4),
                "review_recall": round(r.review_recall, 4),
                "incorrect_autocreate": r.incorrect_autocreate,
            }
        )
    return rows


def print_sweep(rows: list[dict]) -> None:
    SWEEP_JSON.parent.mkdir(parents=True, exist_ok=True)
    SWEEP_JSON.write_text(json.dumps(rows, indent=2))
    try:
        from rich.console import Console
        from rich.table import Table

        t = Table(title="Auto-create threshold sweep", title_style="bold")
        t.add_column("threshold", justify="right")
        t.add_column("auto-create rate", justify="right")
        t.add_column("auto-create precision", justify="right")
        t.add_column("review recall", justify="right")
        t.add_column("incorrect auto-created POs", justify="right")
        for r in rows:
            t.add_row(
                f"{r['threshold']:.2f}",
                f"{r['auto_create_rate']*100:.1f}%",
                f"{r['auto_create_precision']*100:.1f}%",
                f"{r['review_recall']*100:.1f}%",
                str(r["incorrect_autocreate"]),
            )
        Console().print(t)
    except ImportError:
        print(f"{'thr':>5} {'auto%':>7} {'prec%':>7} {'recall%':>8} {'bad':>4}")
        for r in rows:
            print(
                f"{r['threshold']:>5.2f} {r['auto_create_rate']*100:>7.1f} "
                f"{r['auto_create_precision']*100:>7.1f} {r['review_recall']*100:>8.1f} "
                f"{r['incorrect_autocreate']:>4}"
            )
    print(f"sweep written to {SWEEP_JSON}")


if __name__ == "__main__":  # pragma: no cover
    print_sweep(run_sweep())
