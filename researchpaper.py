import os
import requests
import time
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def navigate_to_date(driver, target_date):
    current_url = driver.current_url
    date_param = f"date={target_date}"
    if "date=" in current_url:
        new_url = re.sub(r'date=\d{4}-\d{2}-\d{2}', date_param, current_url)
    else:
        new_url = f"{current_url}{'&' if '?' in current_url else '?'}{date_param}"
    
    driver.get(new_url)
    logger.info(f"Navigated to papers for date: {target_date}")

def setup_driver(headless=True):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(options=options)

def download_pdf(pdf_url, filename):
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        logger.info(f"PDF downloaded successfully as '{filename}'")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to download PDF for '{filename}'. Error: {e}")
        return False

def get_safe_filename(title, href):
    if title and title.strip():
        safe_title = re.sub(r'[^\w\-_\. ]', '', title)
        safe_title = safe_title.strip()
        if safe_title:
            return safe_title[:200] + '.pdf'  # Limit filename length
    
    # If title is empty or becomes empty after sanitization, use href
    href_parts = href.split('/')
    return href_parts[-1][:200] + '.pdf'  # Limit filename length

def process_paper(driver, paper_link, download_dir):
    href = paper_link.get_attribute('href')
    title = paper_link.text.strip()
    filename = get_safe_filename(title, href)
    
    logger.info(f"Processing: {title or href}")
    
    try:
        # Open paper in new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(href)
        
        # Wait for the "View PDF" button to be clickable
        wait = WebDriverWait(driver, 20)
        pdf_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'btn') and contains(text(), 'View PDF')]")))
        pdf_url = pdf_button.get_attribute('href')
        
        # Download PDF
        return download_pdf(pdf_url, os.path.join(download_dir, filename))
    except TimeoutException:
        logger.warning(f"Timeout while processing paper: {title or href}")
    except NoSuchElementException:
        logger.warning(f"Could not find PDF button for paper: {title or href}")
    except WebDriverException as e:
        logger.error(f"WebDriver exception for paper {title or href}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing paper {title or href}: {e}")
    finally:
        # Close the tab and switch back to main tab
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    
    return False

def download_papers(target_date=None, max_retries=3, scroll_pause_time=5, headless=True, paper_limit=None):
    driver = setup_driver(headless)
    processed_hrefs = set()
    total_papers = 0
    retry_count = 0
    
    try:
        driver.get("https://huggingface.co/papers")
        logger.info("Navigated to Hugging Face papers page")
        
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")
        navigate_to_date(driver, target_date)
        
        download_dir = os.path.join('downloaded_papers', target_date)
        os.makedirs(download_dir, exist_ok=True)
        logger.info(f"Downloading papers to: {download_dir}")
        
        while True:
            paper_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'cursor-pointer') and contains(@href, '/papers/')]")
            
            new_papers = False
            for link in paper_links:
                if paper_limit is not None and total_papers >= paper_limit:
                    logger.info(f"Reached the specified limit of {paper_limit} papers. Stopping download.")
                    return download_dir

                href = link.get_attribute('href')
                if href not in processed_hrefs:
                    if process_paper(driver, link, download_dir):
                        processed_hrefs.add(href)
                        new_papers = True
                        total_papers += 1
                        logger.info(f"Total papers processed: {total_papers}")
            
            if not new_papers:
                logger.info("No new papers found. Attempting to scroll...")
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    retry_count += 1
                    if retry_count > max_retries:
                        logger.info("Reached the end of the page. Exiting.")
                        break
                    else:
                        logger.info(f"No new content loaded. Retry {retry_count}/{max_retries}")
                else:
                    retry_count = 0
            else:
                retry_count = 0
            
            logger.info(f"Processed {len(processed_hrefs)} papers so far.")
        
        logger.info(f"Download complete. Total papers downloaded: {total_papers}")
        return download_dir
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        driver.quit()
        logger.info("Browser closed")

if __name__ == "__main__":
    # This allows the script to be run independently for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Download research papers from Hugging Face.")
    parser.add_argument("-d", "--date", help="Target date in YYYY-MM-DD format. If not provided, current date will be used.")
    parser.add_argument("-n", "--number", type=int, help="Number of papers to download. If not provided, all available papers will be downloaded.")
    parser.add_argument("--no-headless", action="store_true", help="Run the browser in non-headless mode (visible browser window).")
    
    args = parser.parse_args()
    
    download_papers(
        target_date=args.date,
        paper_limit=args.number,
        headless=not args.no_headless
    )