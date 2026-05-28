import sys
import os
from loguru import logger

logger.remove()

logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
    level="INFO",
    serialize=False,
    colorize=False,
)

def setup_sentry():
    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        import sentry_sdk
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.1,
            environment=os.getenv("RAILWAY_ENVIRONMENT_NAME", "development"),
        )
        logger.info("Sentry initialized")
    else:
        logger.warning("SENTRY_DSN not set — error tracking disabled")