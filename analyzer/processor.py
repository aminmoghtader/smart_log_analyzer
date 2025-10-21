from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from .parser import LogParser, MalformedLogEntryError
import logging
from typing import List, Optional, Dict, Any
from .file_utils import iter_log_files

logging.basicConfig(
    filename="analyzer_app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def aggregate_stats(parsed_iter: List[Optional[Dict[str, Any]]], \
                    source_path: str = ""):
    """Build aggregated statistics from parsed log lines."""
    total_lines = 0
    malformed_lines = 0
    daily_stats: Dict[str, Counter] = defaultdict(Counter)
    total_errors = 0
    total_warnings = 0

    for item in parsed_iter:
        total_lines += 1
        if not item:
            malformed_lines += 1
            continue

        ts = item.get("timestamp")
        lvl = (item.get("level") or "").upper().strip()
        if not ts or not lvl:
            malformed_lines += 1
            continue

        try:
            dt = datetime.fromisoformat(ts.replace(" ", "T"))
            day = dt.strftime("%Y-%m-%d")
        except Exception:
            malformed_lines += 1
            continue

        daily_stats[day][lvl] += 1
        if lvl in ("ERROR", "CRITICAL"):
            total_errors += 1
        elif lvl in ("WARN", "WARNING"):
            total_warnings += 1

    daily_stats_dict = {k: dict(v) for k, v in daily_stats.items()}

    return {
        "metadata": {
            "report_generated_at": datetime.now().isoformat(),
            "source_path": source_path,
            "total_files_processed": 0,  # will set later
            "total_lines_processed": total_lines,
        },
        "daily_stats": daily_stats_dict,
        "overall_summary": {
            "total_errors_and_criticals": total_errors,
            "total_warnings": total_warnings,
            "malformed_lines_count": malformed_lines
        }
    }

def aggregate_stats_from_files(paths: str):
    """Parse log files and aggregate statistics."""
    parser = LogParser()
    parsed_items: List[Optional[Dict[str, Any]]] = []
    files = list(iter_log_files(paths))

    for fp in files:
        with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                try:
                    parsed = parser.parse(line)
                    parsed_items.append(parsed)
                except MalformedLogEntryError:
                    parsed_items.append(None)

    report = aggregate_stats(parsed_items, source_path=paths)
    report["metadata"]["total_files_processed"] = len(files)
    return report
