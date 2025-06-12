import csv
import argparse
import time
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

AREA_CODES = ["6001001000", "6001002000", "6001005000", "6001006000", "6001008000"]


def launch_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def build_search_url(keyword: str, page: int) -> str:
    areas = "%2C".join(AREA_CODES)
    return (
        f"https://www.104.com.tw/jobs/search/?keyword={keyword}"
        f"&area={areas}&page={page}&jobsource=2018indexpoc"
    )


def is_valid_salary(text: str) -> bool:
    return any(char.isdigit() for char in text)


def parse_job(card) -> Dict[str, str]:
    jobname = card.find_element(By.CSS_SELECTOR, "a.js-job-link").text.strip()
    company = card.find_element(By.CSS_SELECTOR, "ul.job-list-intro li > a").text.strip()
    location = card.find_element(By.CSS_SELECTOR, "ul.job-list-intro li").text.strip()
    link = card.find_element(By.CSS_SELECTOR, "a.js-job-link").get_attribute("href")
    salary_el = card.find_elements(By.CSS_SELECTOR, "span.b-tag--default")
    salary = salary_el[-1].text.strip() if salary_el else ""
    jtype_el = card.find_elements(By.CSS_SELECTOR, "span.b-tit__info")
    jtype = jtype_el[0].text.strip() if jtype_el else ""
    desc_el = card.find_elements(By.CSS_SELECTOR, "p.job-list-item__info")
    desc = desc_el[0].text.strip() if desc_el else ""
    return {
        "Job Title": jobname,
        "Company Name": company,
        "Job Location": location,
        "Salary": salary,
        "Job Type": jtype,
        "Job Description": desc,
        "Job URL": link,
    }


def crawl(keyword: str, minimum: int = 300, pages_per_round: int = 3) -> List[Dict[str, str]]:
    driver = launch_driver()
    results: List[Dict[str, str]] = []
    page = 1
    try:
        while len(results) < minimum:
            for _ in range(pages_per_round):
                url = build_search_url(keyword, page)
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article.job-list-item"))
                )
                cards = driver.find_elements(By.CSS_SELECTOR, "article.job-list-item")
                for card in cards:
                    try:
                        data = parse_job(card)
                        if is_valid_salary(data["Salary"]):
                            results.append(data)
                    except Exception:
                        continue
                page += 1
                time.sleep(1)
                if len(results) >= minimum:
                    break
            if page > 100:  # safety
                break
    finally:
        driver.quit()
    return results


def save_csv(data: List[Dict[str, str]], keyword: str) -> str:
    filename = f"job_data_104_{keyword.replace(' ', '')}_filtered.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Job Title",
                "Company Name",
                "Job Location",
                "Salary",
                "Job Type",
                "Job Description",
                "Job URL",
            ],
        )
        writer.writeheader()
        writer.writerows(data)
    return filename


def main():
    parser = argparse.ArgumentParser(description="Scrape job data from 104.com.tw")
    parser.add_argument("keyword", help="Job title keyword")
    parser.add_argument("--min", dest="minimum", type=int, default=300, help="Minimum records")
    args = parser.parse_args()
    jobs = crawl(args.keyword, minimum=args.minimum)
    save_csv(jobs, args.keyword)


if __name__ == "__main__":
    main()
