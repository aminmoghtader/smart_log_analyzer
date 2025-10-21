import re, json
from datetime import datetime
import logging

class MalformedLogEntryError(Exception):
    pass

LEVELS = ("ERROR","CRITICAL","WARN","WARNING","INFO","DEBUG")
TS_RE = re.compile(r"\[?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]?")

class LogParser:
    def parse(self, line: str):
        s = line.strip()
        if not s:
            logging.warning("Empty line encountered in parser")
            raise MalformedLogEntryError("Empty line")

        if s.startswith("{") and s.endswith("}"):
            try:
                obj = json.loads(s)
                ts = obj.get("timestamp") or obj.get("time")
                lvl = (obj.get("level") or obj.get("severity") or "").upper() or None
                msg = obj.get("message") or obj.get("msg") or str(obj)
                if not ts or not lvl:
                    raise MalformedLogEntryError("Missing timestamp or level")
                return {"timestamp": self._normalize_ts(ts), "level": lvl, \
                        "message": str(msg)}
            except Exception as e:
                logging.warning(f"JSON parse error: {e}")
                raise MalformedLogEntryError("Invalid JSON line")

        ts_match = TS_RE.search(s)
        ts = self._normalize_ts(ts_match.group(1)) if ts_match else None
        lvl = self._find_level(s)
        msg = s

        if lvl:
            msg = re.sub(rf"\[?{lvl}\]?", "", msg, flags=re.I).strip()
            if ts_match:
                msg = msg.replace(ts_match.group(0), "").strip()
            msg = msg.lstrip(":- ")
        elif ":" in msg:
            msg = msg.split(":",1)[1].strip()

        if not ts or not lvl:
            logging.warning(f"Malformed log line: {s}")
            raise MalformedLogEntryError("Missing timestamp or level")

        return {"timestamp": ts, "level": lvl, "message": msg}

    def _find_level(self, line: str):
        for lvl in LEVELS:
            if re.search(rf"\[?{lvl}\]?", line, re.I):
                return lvl.upper()
        return None

    def _normalize_ts(self, ts_str: str):
        try:
            dt = datetime.fromisoformat(ts_str.replace(" ", "T"))
            return dt.isoformat()
        except Exception:
            return ts_str
