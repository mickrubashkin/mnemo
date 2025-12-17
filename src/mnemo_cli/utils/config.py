import json
from pathlib import Path
from datetime import timezone, datetime

from mnemo_cli.enums import Language, Source


def save_config(
        project_root: Path,
        *,
        sources: set[Source],
        languages: set[Language],
        ) -> None:
    mnemo_dir = project_root / ".mnemo"

    config_path = mnemo_dir / "config.json"
    created_at = datetime.now(timezone.utc).isoformat()
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                created_at = json.load(f).get("created_at", created_at)
            except Exception:
                pass

    config = {
        "sources": [s.value for s in sources],
        "languages": [l.value for l in languages],
        "created_at": created_at,
        "last_indexed_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(mnemo_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)



def load_config(project_root: Path) -> dict:
    config_path = project_root / ".mnemo" / "config.json"
    if not config_path.exists():
        raise RuntimeError("mnemo config not found. Run `mnemo init` first.")

    with open(config_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    try:
        sources = {Source(code) for code in raw.get("sources", [])}
        languages = {Language(code) for code in raw.get("languages", [])}
        created_at = datetime.fromisoformat(raw["created_at"])
        last_indexed_at = datetime.fromisoformat(raw["last_indexed_at"])
    except Exception as e:
        raise RuntimeError(f"Invalid mnemo config format: {e}")

    return {
        "sources": sources,
        "languages": languages,
        "created_at": created_at,
        "last_indexed_at": last_indexed_at,
    }
