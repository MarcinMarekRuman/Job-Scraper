import requests
import pandas as pd
import time
import json

BASE_URL = "https://nofluffjobs.com/api"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def fetch_jobs(keyword="python", page=1, page_size=20):
    url = f"{BASE_URL}/search/posting"
    params = {
        "limit": page_size,
        "offset": (page - 1) * page_size,
        "salaryCurrency": "PLN",
        "salaryPeriod": "month",
        "region": "pl",
    }

    payload = {
        "criteriaSearch": {
            "requirement": [keyword],
        },
        "page": page,
        "pageSize": page_size,
    }

    response = requests.post(url, json=payload, params=params,headers=HEADERS, timeout=15)
    print(f"Status: {response.status_code}")
    response.raise_for_status()

    data = response.json()


    with open("debug_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data

def parse_offer(job: dict) -> dict:
    salary = job.get("salary") or {}
    location = job.get("location") or {}
    places = location.get("places", [])


    cities = [
        p.get("city") for p in places
        if p.get("city") and p.get("city") != "Remote"
    ]
    city = cities[0] if cities else "Remote"
    is_remote = any(p.get("city") == "Remote" for p in places)


    technologies = job.get("technology", [])
    if isinstance(technologies, list):
        tech_str = ", ".join(technologies)
    else:
        tech_str = str(technologies)

    return {
        "id": job.get("id"),
        "title": job.get("title"),
        "company": job.get("name"),
        "city": city,
        "remote": is_remote,
        "salary_from": salary.get("from"),
        "salary_to": salary.get("to"),
        "currency": salary.get("currency"),
        "salary_type": salary.get("type"),
        "technologies": tech_str,
        "seniority": ", ".join(job.get("seniority", [])),
        "url": f"https://nofluffjobs.com/pl/job/{job.get('url')}",
        "posted": job.get("posted"),
    }

def scrape_jobs(keyword="python", max_pages=5):
    all_jobs = []

    first = fetch_jobs(keyword, page=1)
    total = first.get("totalCount", 0)
    print(f"Znaleziono łącznie: {total} ofert\n")

    for job in first.get("postings", []):
        all_jobs.append(parse_offer(job))
        if len(all_jobs) >= 100:
            break

    for page in range(2, max_pages + 1):
        if len(all_jobs) >= 100:
            break
        print(f"Pobieranie strony {page}...")
        data = fetch_jobs(keyword, page=page)
        for job in data.get("postings", []):
            all_jobs.append(parse_offer(job))
            if len(all_jobs) >= 100:
                break
        time.sleep(1)

    return all_jobs[:100]

if __name__ == "__main__":
    jobs = scrape_jobs(keyword="python", max_pages=5)

    if jobs:
        df = pd.DataFrame(jobs)
        df.to_csv("data/jobs.csv", index=False, encoding="utf-8")
        print(f"\nZapisano {len(jobs)} ofert do data/jobs.csv")
        print(df.head(10).to_string())
    else:
        print("Brak danych — sprawdź debug_response.json")