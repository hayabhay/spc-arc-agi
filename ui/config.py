import os
import tempfile
from pathlib import Path

# Project structure
# -----------------
APP_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = APP_DIR.parent.absolute()
TEMP_DIR = Path(tempfile.gettempdir())
LOGS_DIR = PROJECT_DIR / "logs"
# Data paths
DATA_DIR = PROJECT_DIR / "data"
ORIG_DATASET = DATA_DIR / "original"

# Load filenames of evaluation & training data from original set
EVAL_FPATHS = list((ORIG_DATASET / "evaluation").rglob("*.json"))
EVAL_TASKIDS = set([fpath.name.split(".")[0] for fpath in EVAL_FPATHS])
TRAIN_FPATHS = list((ORIG_DATASET / "training").rglob("*.json"))
TRAIN_TASKIDS = set([fpath.name.split(".")[0] for fpath in TRAIN_FPATHS])

print(TRAIN_FPATHS[:10])

# Environment variables
# ---------------------
DEV = os.environ.get("DEV", False)

# Common page configurations
# --------------------------
ABOUT = """
### Streamlit UI

Please report any bugs or issues on
[Github](https://github.com/hayabhay/fastapi-streamlit-starter/issues). Thanks!
"""


def get_page_config(page_title_prefix="", layout="wide"):
    return {
        "page_title": f"{page_title_prefix} FastAPI Streamlit Starter",
        "page_icon": "🔀",
        "layout": layout,
        "initial_sidebar_state": "expanded",
        "menu_items": {
            "Get Help": "https://twitter.com/hayabhay",
            "Report a bug": "https://github.com/hayabhay/fastapi-streamlit-starter/issues",
            "About": ABOUT,
        },
    }


def init_session(session_state, reset: bool = False):
    """Site wide function to intialize session state variables if they don't exist."""
    # Session states
    # --------------------------------
    pass
