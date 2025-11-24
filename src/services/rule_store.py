from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class DomainRule:
    host: str
    path_pattern: str
    version: int
    card_selector: str
    fields: Dict[str, str]
    dom_signature: str
    success_count: int = 0


class RuleStore:
    """Minimal JSON-backed rule store with a file lock.

    For Railway, mount a Volume at /data and point RULES_PATH there.
    """

    def __init__(self, rules_path: Optional[str] = None):
        self.rules_path = rules_path or os.environ.get("RULES_PATH", "rules.json")
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self) -> None:
        path = Path(self.rules_path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}", encoding="utf-8")

    def _load(self) -> Dict[str, Any]:
        with self._lock:
            raw = Path(self.rules_path).read_text(encoding="utf-8")
            try:
                return json.loads(raw or "{}")
            except Exception:
                return {}

    def _save(self, data: Dict[str, Any]) -> None:
        with self._lock:
            Path(self.rules_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_for_host(self, host: str) -> List[DomainRule]:
        data = self._load()
        items = data.get(host, [])
        return [DomainRule(**it) for it in items]

    def upsert(self, rule: DomainRule) -> None:
        data = self._load()
        items = data.get(rule.host, [])
        # Replace on same path_pattern; keep highest version
        replaced = False
        for i, it in enumerate(items):
            if it.get("path_pattern") == rule.path_pattern:
                if rule.version >= it.get("version", 0):
                    items[i] = asdict(rule)
                replaced = True
                break
        if not replaced:
            items.append(asdict(rule))
        data[rule.host] = items
        self._save(data)
