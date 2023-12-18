import requests
import csv
from typing import List, Dict
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright

payload = {}

headers_2 = {
  'authority': 'www1.communitech.ca',
  'accept': 'application/json',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'cookie': '_ga=GA1.1.518693555.1698001341; ajs_anonymous_id=75fceede-155b-442a-9f53-70c5d8141f4c; ajs_group_id=collection_628; wooTracker=yohzMUXqBjgY; _hjSessionUser_2813421=eyJpZCI6IjczOTQ0ZWUzLTcyYmEtNTBjYS04MjAzLTcxODQ5MjBjMGIzMSIsImNyZWF0ZWQiOjE2OTgwMDEzNDEwMjksImV4aXN0aW5nIjpmYWxzZX0=; _hjFirstSeen=1; _hjIncludedInSessionSample_2813421=0; _hjSession_2813421=eyJpZCI6ImNmZmJmMmMwLTRhNGItNDZlZS04NmNiLTgwZjdjN2E5Mjc2NSIsImNyZWF0ZWQiOjE2OTgwMDEzNDEwMzAsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6ZmFsc2V9; fs_lua=1.1698001341059; fs_uid=^#16BDZT^#969dcf74-e0d4-4085-ba1a-c9b4db20e34e:fae9dfa9-d285-48d7-8288-6bb80ce4ddda:1698001341059::1^#/1729537340; _ga_HEMR7K1WFM=GS1.1.1698001340.1.0.1698001348.0.0.0',
  'dnt': '1',
  'pragma': 'no-cache',
  'referer': 'https://www1.communitech.ca/companies',
  'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}
def fetch_company_data(base_url: str, total_pages: int) -> List[List[str]]:
    company_data = []

    for page_number in range(0, total_pages + 1):
        api_url = f"{base_url}{page_number}"
        response = requests.get(api_url, headers=headers_2, data=payload)  

        if response.status_code == 200:
            data = response.json()
            companies = data["hits"]

            for company in companies:
                name = company.get("name", "")
                description = company.get("description", "")
                locations = ", ".join(company.get("locations", []))
                logo_url = company.get("logo_url", "")
                topics = ", ".join(company.get("topics", []))
                industry_tags = ", ".join(company.get("industry_tags", []))
                stage = company.get("stage", "")
                head_count = company.get("head_count", 0)
                active_jobs_count = company.get("active_jobs_count", 0)

                company_data.append([name, description, locations, logo_url, topics, industry_tags, stage, head_count, active_jobs_count])
        else:
            print(f"Error: Unable to fetch data for page {page_number} (Status Code: {response.status_code})")

    return company_data

def save_company_data_to_csv(company_data: List[List[str]], filename: str) -> None:
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Description', 'Locations', 'Logo URL', 'Topics', 'Industry Tags', 'Stage', 'Head Count', 'Active Jobs Count'])
        writer.writerows(company_data)
    print("Data has been successfully saved to companies.csv.")

base_url = "https://www1.communitech.ca/api/search/companies?networkId=628&hitsPerPage=12&page="
total_pages = 145
company_data = fetch_company_data(base_url, total_pages)
save_company_data_to_csv(company_data, 'companies.csv')
def get_cookies():
    pass

def fetch_job_data(base_url: str, total_pages: int) -> List[Dict[str, str]]:
    jobs_data = []

    for page_number in range(0, total_pages + 1):
        api_url = f"{base_url}{page_number}&filters=&query="
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            results = data["results"]

            for result in results:
                hits = result["hits"]

                for job in hits:
                    job_details = {
                        "created_at": job.get("created_at", ""),
                        "locations": job.get("locations", ""),
                        "organization_id": job["organization"]["id"],
                        "organization_name": job["organization"]["name"],
                        "organization_logo_url": job["organization"]["logo_url"],
                        "organization_slug": job["organization"]["slug"],
                        "organization_topics": ", ".join(job["organization"]["topics"]),
                        "organization_industry_tags": ", ".join(job["organization"]["industry_tags"]),
                        "organization_stage": job["organization"]["stage"],
                        "organization_head_count": job["organization"]["head_count"],
                        "source": job.get("source", ""),
                        "slug": job.get("slug", ""),
                        "title": job.get("title", ""),
                        "url": job.get("url", ""),
                        "featured": job.get("featured", ""),
                        "has_description": job.get("has_description", "")
                    }
                    jobs_data.append(job_details)
        else:
            print(f"Error: Unable to fetch data for page {page_number} (Status Code: {response.status_code})")

    return jobs_data

def save_data_to_csv(jobs_data: List[Dict[str, str]], file_path: str) -> None:
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Created At', 'Locations', 'Organization ID', 'Organization Name', 'Organization Logo URL',
                         'Organization Slug', 'Organization Topics', 'Organization Industry Tags', 'Organization Stage',
                         'Organization Head Count', 'Source', 'Slug', 'Title', 'URL', 'Featured', 'Has Description'])
        for job in jobs_data:
            writer.writerow( job["created_at"], job["locations"], job["organization_id"], job["organization_name"],
                             job["organization_logo_url"], job["organization_slug"], job["organization_topics"],
                             job["organization_industry_tags"], job["organization_stage"], job["organization_head_count"],
                             job["source"], job["slug"], job["title"], job["url"], job["featured"], job["has_description"])

base_url = "https://www1.communitech.ca/api/search/jobs?networkId=628&hitsPerPage=20&page="
total_pages = 300
jobs_data = fetch_job_data(base_url, total_pages)
save_data_to_csv(jobs_data, 'jobs.csv')
print("Data has been successfully saved to Jobs.csv.")

jobs = pd.read_csv("jobs.csv")
jobs.columns = ['created_at', 'locations', 'organization_id', 'organization_name',
                'organization_logo_url', 'organization_slug', 'organization_topics',
                'organization_industry_tags', 'organization_stage',
                'organization_head_count', 'source', 'slug', 'title', 'url', 'featured',
                'has_description']
jobs['url'] = 'https://www1.communitech.ca/companies/' + jobs['organization_slug'] + '/jobs/' + jobs['slug'] + '#content'
jobs = jobs[jobs['has_description'] == True]
jobs = jobs[['organization_name', 'title', 'locations', 'organization_topics', 'organization_industry_tags', 'url', 'has_description']]
print(jobs.shape)

for url in jobs['url']:
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    career_page_div = soup.find('div', {'data-testid': 'careerPage'})

    if career_page_div is not None:
        jobs.loc[jobs['url'] == url, 'description'] = str(career_page_div)
    else:
        jobs.loc[jobs['url'] == url, 'description'] = ''

jobs.to_csv('jobs_info.csv', index=False)