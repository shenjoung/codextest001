# codextest001

This repository demonstrates a job crawler for 104.com.tw.

## crawler.py

`crawler.py` is a simple example using `requests` and `BeautifulSoup` which may no longer work because 104.com.tw renders pages with JavaScript.

## selenium_crawler.py

`selenium_crawler.py` launches a headless Chrome browser with Selenium and collects job listings that include numeric salary information. The program accepts a job title keyword and writes the results to a CSV file whose name contains that keyword. It automatically filters for jobs in Taipei, New Taipei, Taoyuan, Hsinchu and Miaoli.

```
python selenium_crawler.py "Data Analyst" --min 300
```

Actual crawling may fail if network access to 104.com.tw is blocked in the environment.
