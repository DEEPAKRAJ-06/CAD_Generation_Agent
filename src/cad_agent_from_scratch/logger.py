"""
Central logging configuration for CAD Agent from Scratch.

Logs are always written to:
<project_root>/logs/

Safe for:
- Jupyter notebooks
- LangGraph Studio
- CLI execution
"""

import logging
import os
from datetime import datetime

# =============================================================================
# PROJECT ROOT RESOLUTION (IMPORTANT)
# =============================================================================

# This file lives in: src/cad_agent_from_scratch/logger.py
# Project root is two levels up
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# =============================================================================
# LOG FILE SETUP
# =============================================================================

LOG_FILE_NAME = f"cad_agent_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"
LOG_FILE_PATH = os.path.join(LOGS_DIR, LOG_FILE_NAME)

# =============================================================================
# LOGGER CONFIGURATION
# =============================================================================

logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format=(
        "[%(asctime)s] "
        "[%(levelname)s] "
        "[%(name)s:%(lineno)d] "
        "%(message)s"
    ),
)

# =============================================================================
# CONSOLE OUTPUT (Notebook + CLI)
# =============================================================================

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_formatter = logging.Formatter(
    "[%(levelname)s] %(name)s - %(message)s"
)
console_handler.setFormatter(console_formatter)

root_logger = logging.getLogger()
if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
    root_logger.addHandler(console_handler)

# =============================================================================
# INIT LOG
# =============================================================================

logging.info("CAD Agent logger initialized")
logging.info(f"Project root: {PROJECT_ROOT}")
logging.info(f"Log file: {LOG_FILE_PATH}")