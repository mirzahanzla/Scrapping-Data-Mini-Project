import time
import logging
import json
import threading
from datetime import datetime
import schedule
from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------- Flask Setup -----------------------
app = Flask(__name__)
CORS(app)

# ----------------------- Logging Setup -----------------------
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ----------------------- WebDriver Setup -----------------------
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service()  # Ensure chromedriver is in PATH
    return webdriver.Chrome(service=service, options=chrome_options)

# ----------------------- Scrape Logic -----------------------
def scrape_jobs():
    logging.info("Scraping started.")
    driver = setup_driver()
    driver.get("https://www.actuarylist.com/")

    time.sleep(5)  # Allow page to load

    scraped_jobs_data = []
    try:
        wait = WebDriverWait(driver, 20)
        job_cards = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "article .Job_job-card__YgDAV.Job_job-card-active__6V_ep")
        ))

        for idx, card in enumerate(job_cards, start=1):
            try:
                title = card.find_element(By.CSS_SELECTOR, "p.Job_job-card__position__ic1rc").text.strip()
                company = card.find_element(By.CSS_SELECTOR, "p.Job_job-card__company__7T9qY").text.strip()
                location = card.find_element(By.CSS_SELECTOR, "a.Job_job-card__location__bq7jX").text.strip()
                country = card.find_element(By.CSS_SELECTOR, "div .Job_job-card__country__GRVhK").text.strip()
                scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                scraped_jobs_data.append({
                    'id': idx,
                    'title': title,
                    'company': company,
                    'location': location,
                    'country': country,
                    'scraped_at': scraped_at
                })
            except Exception as e:
                logging.warning(f"Failed to parse job card: {str(e)}")

    except Exception as e:
        logging.error(f"Error during scraping: {str(e)}")

    finally:
        driver.quit()

        with open('jobs.json', 'w') as json_file:
            json.dump(scraped_jobs_data, json_file, indent=4)

        logging.info(f"Scraping ended. Total jobs scraped: {len(scraped_jobs_data)}")
        print(f"✅ Total job articles scraped: {len(scraped_jobs_data)}")

# ----------------------- API Routes -----------------------
@app.route('/jobs', methods=['GET'])
def get_jobs():
    try:
        with open('jobs.json', 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        logging.error(f"Failed to read jobs.json: {str(e)}")
        return jsonify({"error": "Could not read job data"}), 500

@app.route('/jobs', methods=['POST'])
def add_job():
    try:
        new_job = request.get_json()
        with open('jobs.json', 'r+') as f:
            jobs = json.load(f)
            max_id = max((job.get("id", 0) for job in jobs), default=0)
            new_job['id'] = max_id + 1
            new_job['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            jobs.append(new_job)
            f.seek(0)
            json.dump(jobs, f, indent=4)
        logging.info(f"Job added: {new_job}")
        return jsonify(new_job), 201
    except Exception as e:
        logging.error(f"Error adding job: {str(e)}")
        return jsonify({"error": "Could not add job"}), 500

@app.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        with open('jobs.json', 'r+') as f:
            jobs = json.load(f)
            job_to_delete = next((job for job in jobs if job['id'] == job_id), None)
            if not job_to_delete:
                return jsonify({"error": "Job not found"}), 404
            jobs = [job for job in jobs if job['id'] != job_id]
            f.seek(0)
            f.truncate()
            json.dump(jobs, f, indent=4)
        logging.info(f"Job deleted: {job_id}")
        return jsonify({"message": "Job deleted"}), 200
    except Exception as e:
        logging.error(f"Error deleting job: {str(e)}")
        return jsonify({"error": "Could not delete job"}), 500

# ----------------------- Scheduler -----------------------
def run_scheduler():
    schedule.every(3).minutes.do(scrape_jobs)  # for testing
    # Production:
    schedule.every().day.at("00:00").do(scrape_jobs)
    schedule.every().day.at("03:00").do(scrape_jobs)
    schedule.every().day.at("06:00").do(scrape_jobs)

    logging.info("Scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(1)

# ----------------------- Main Execution -----------------------
if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=True)
