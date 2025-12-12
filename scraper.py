import argparse
import csv
import hashlib
import os
import requests
import time

# CSV paths
MASTER = "master_jobs.csv"
DELTA = "delta_jobs.csv"

TIMEOUT = 10
HEADERS = {"User-Agent": "Mozilla/5.0"}

# VERIFIED working Lever companies (2025)
LEVER_COMPANIES = [
    "sentry",
    "zapier",
    "remote",
    "retool",
    "clearbit",
    "pilot",
    "cerebras"
]

# VERIFIED working Ashby companies (2025)
ASHBY_COMPANIES = [
    "mistralai",
    "cohere",
    "runway",
    "adept",
    "instadeep",
    "character",
    "luma"
]


def hash_id(text):
    return hashlib.sha256(text.encode()).hexdigest()


def load_existing_ids():
    if not os.path.exists(MASTER):
        return set()
    with open(MASTER, encoding="utf-8") as f:
        return {row["id"] for row in csv.DictReader(f)}


def save_csv(path, rows):
    header = ["job_title", "company", "location", "description", "url", "id"]
    write_header = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if write_header:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)


def matches_query(job_text, query_terms):
    job_text = job_text.lower()
    return any(q.lower() in job_text for q in query_terms)


# ------------ Lever Scraper ------------
def scrape_lever(slug, query_terms):
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return jobs
        data = resp.json()
    except:
        return jobs

    for item in data:
        title = item.get("text", "")
        link = item.get("hostedUrl", "")
        desc = item.get("descriptionPlain", "") or ""
        cats = item.get("categories", {}) or {}
        location = cats.get("location", "")

        combined = f"{title} {location} {desc}"

        if not matches_query(combined, query_terms):
            continue

        if not link:
            continue

        jobs.append({
            "job_title": title,
            "company": slug,
            "location": location,
            "description": desc[:400],
            "url": link,
            "id": hash_id(link)
        })

    return jobs


# ------------ Ashby Scraper ------------
def scrape_ashby(slug, query_terms):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    jobs = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return jobs
        data = resp.json()
    except:
        return jobs

    postings = data.get("jobs", [])

    for item in postings:
        title = item.get("title", "")
        job_id = item.get("id", "")
        desc = item.get("descriptionText", "") or ""
        loc = ", ".join(item.get("locations", [])) if isinstance(item.get("locations"), list) else ""

        url = f"https://jobs.ashbyhq.com/{slug}/job/{job_id}"

        combined = f"{title} {loc} {desc}"

        if not matches_query(combined, query_terms):
            continue

        jobs.append({
            "job_title": title,
            "company": slug,
            "location": loc,
            "description": desc[:400],
            "url": url,
            "id": hash_id(url)
        })

    return jobs


# ------------ MAIN ------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    args = parser.parse_args()

    # example: "AI engineer europe remote"
    query_terms = args.query.lower().split()

    existing_ids = load_existing_ids()
    print(f"[INFO] Loaded {len(existing_ids)} existing job IDs")
    print(f"[INFO] Query terms: {query_terms}\n")

    all_jobs = []

    print("[INFO] Scraping Lever...")
    for slug in LEVER_COMPANIES:
        jobs = scrape_lever(slug, query_terms)
        print(f"  {slug}: {len(jobs)} matches")
        all_jobs.extend(jobs)
        time.sleep(0.2)

    print("\n[INFO] Scraping Ashby...")
    for slug in ASHBY_COMPANIES:
        jobs = scrape_ashby(slug, query_terms)
        print(f"  {slug}: {len(jobs)} matches")
        all_jobs.extend(jobs)
        time.sleep(0.2)

    print(f"\n[INFO] Total scraped: {len(all_jobs)}")

    # Compute new (delta)
    new_jobs = [j for j in all_jobs if j["id"] not in existing_ids]
    print(f"[INFO] New jobs: {len(new_jobs)}")

    if new_jobs:
        save_csv(MASTER, new_jobs)
        save_csv(DELTA, new_jobs)
        print("[INFO] Saved to master_jobs.csv and delta_jobs.csv\n")

        print("[PREVIEW]")
        for job in new_jobs[:10]:
            print(f"- {job['job_title']} | {job['company']} | {job['location']}")
            print(f"  {job['url']}\n")

    else:
        print("[INFO] No new jobs found.\n")


if __name__ == "__main__":
    main()
