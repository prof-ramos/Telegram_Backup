"""
Telegram Backup Service Runner
Runs the backup service in a separate process
"""

import asyncio
import logging
import signal
import sys
import os
from telegram_backup import create_backup_manager

# Configure logging specifically for the service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SERVICE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Backup Service...")

    # Write PID file
    with open("service.pid", "w") as f:
        f.write(str(os.getpid()))

    try:
        manager = create_backup_manager()
        await manager.run_backup_service()
    except Exception as e:
        logger.error(f"Service crashed: {e}")
    finally:
        # Cleanup PID file
        if os.path.exists("service.pid"):
            os.remove("service.pid")
        logger.info("Service Stopped")

def handle_signal(sig, frame):
    logger.info("Received stop signal")
    # Clean exit handled by run_backup_service's run_until_disconnected logic mostly,
    # but we can force exit if needed.
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
