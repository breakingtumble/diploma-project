import os
import sys
from datetime import datetime
import schedule
import time
import logging

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_parsing.parse_products import job
from web_parsing.price_prediction import batch_main as predict_prices

# Configure logging to console only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tasks():
    """Run both parsing and prediction tasks in sequence"""
    try:
        logger.info("Starting product parsing...")
        job()
        logger.info("Product parsing completed successfully")
        
        logger.info("Starting price prediction...")
        predict_prices()
        logger.info("Price prediction completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled tasks: {str(e)}")

def main():
    """Main function to schedule and run tasks"""
    try:
        job()
    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")

    # Schedule tasks to run every 6 hours
    schedule.every(6).hours.do(run_tasks)
    
    # Run immediately on startup
    run_tasks()
    
    logger.info("Scheduler started. Tasks will run every 6 hours.")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(50)  # Check every 50 seconds

if __name__ == "__main__":
    main() 