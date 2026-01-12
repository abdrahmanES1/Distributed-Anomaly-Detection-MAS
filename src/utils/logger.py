import logging
import json
import os
import sys
from logging.handlers import RotatingFileHandler

# Ensure results/logs directory exists
LOG_DIR = "results/logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

class JsonFormatter(logging.Formatter):
    """Formats log records as valid JSON."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "agent_id": getattr(record, "agent_id", "system"),
            "module": record.module,
            "message": record.getMessage(),
        }
        # Add extra fields if they exist
        if hasattr(record, "custom_data"):
            log_record.update(record.custom_data)
            
        return json.dumps(log_record)

def setup_logger(name, agent_id="system"):
    """
    Sets up a logger that writes JSON to a file and formatted text to console.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent double logging

    # Clear existing handlers
    if logger.handlers:
        return logger

    # 1. File Handler (JSON)
    file_handler = RotatingFileHandler(
        f"{LOG_DIR}/agent_activity.jsonl", maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    # 2. Console Handler (Human Readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter(
        f'%(asctime)s - [{agent_id}] - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger
