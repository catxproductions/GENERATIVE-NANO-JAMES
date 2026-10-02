import json
from pathlib import Path
from typing import Any, Dict, Optional

# Base directory where this config.py file is located
BASE_DIR = Path(__file__).resolve().parent

# Default location for preset weights
PRESET_WEIGHTS_PATH = BASE_DIR / "presets" / "weights.json"
ROOT_WEIGHTS_PATH = BASE_DIR / "weights.json"


def load_weights(custom_path: Optional[Path | str] = None) -> Dict[str, Any]:
    """Loads weights from a specified JSON file, falling back to preset locations.

    Args:
        custom_path: Optional custom path to a weights JSON file.

    Returns:
        Dict containing the parsed JSON configuration.

    Raises:
        FileNotFoundError: If no valid weights JSON file is found.
    """
    if custom_path:
        target_path = Path(custom_path)
    elif PRESET_WEIGHTS_PATH.exists():
        target_path = PRESET_WEIGHTS_PATH
    elif ROOT_WEIGHTS_PATH.exists():
        target_path = ROOT_WEIGHTS_PATH
    else:
        raise FileNotFoundError(
            f"Weights file not found. Looked in:\n"
            f" - {PRESET_WEIGHTS_PATH}\n"
            f" - {ROOT_WEIGHTS_PATH}"
        )

    with open(target_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Automatically load configuration when config.py is imported
CONFIG = load_weights()

# Convenience exports for direct access across your app
WEIGHTS = CONFIG.get("weights", {})
PENALTIES = CONFIG.get("penalties", {})
THRESHOLDS = CONFIG.get("thresholds", {})


# Quick verification script if run directly: `python config.py`
if __name__ == "__main__":
    print("Configuration loaded successfully:")
    print(json.dumps(CONFIG, indent=2))
