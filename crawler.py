import requests
from bs4 import BeautifulSoup
import csv

def fetch_jobs(keyword, pages=1):
    result = []
    for page in range(1, pages + 1):
        url = f"https://www.104.com.tw/jobs/search/?page={page}&keyword={keyword}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        job_cards = soup.select("article.job-list-item")
        for job in job_cards:
            jobname = job.select_one("a.js-job-link").text.strip()
            company = job.select_one("ul.job-list-intro > li > a").text.strip()
            location = job.select_one("ul.job-list-intro > li").text.strip()
            result.append({"jobname": jobname, "company": company, "location": location})
    return result


def save_to_csv(data, filename="jobs.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["jobname", "company", "location"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    jobs = fetch_jobs("python", pages=1)
    save_to_csv(jobs)
