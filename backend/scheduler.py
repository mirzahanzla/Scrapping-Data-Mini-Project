# scheduler.py
import schedule
import time
import logging
from scraper import scrape_jobs

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

schedule.every(6).hours.do(scrape_jobs)

while True:
    schedule.run_pending()
    time.sleep(1)
