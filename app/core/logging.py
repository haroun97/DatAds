# Logging configuration for the whole application.
# Call setup_logging() once at startup; all modules then use logging.getLogger(__name__).

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    # Write structured log lines to stdout so container runtimes (Docker, ECS) capture them.
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
