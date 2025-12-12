

## Overview

This is a small Python script that collects job postings from two ATS platforms: **Lever** and **Ashby**.
The script takes a search query as input, pulls public job listings from a set of companies that still use these ATS systems, filters the roles based on the query, and writes the results into two CSV files:

* `master_jobs.csv` — stores every job the scraper has seen.
* `delta_jobs.csv` — stores only the new jobs found during the current run.

This setup makes it easy to track what roles have been added since the last execution.

---

## How it Works

1. The script loads any previously saved job IDs from `master_jobs.csv`.
2. It fetches job postings from Lever and Ashby using their public job-board APIs.
3. It applies basic keyword filtering using the query provided through `--query`.
4. Each job is hashed to create a stable unique ID.
5. Jobs not already present in the master file are marked as new and written to both CSV files.

The script does not scrape HTML. Both ATS platforms provide JSON endpoints exposed publicly, which simplifies the data extraction.

---

## Requirements

Install dependencies:

```
pip install requests
```

Python 3.8+ is recommended.

---

## Running the Script

Pass your search terms via the `--query` flag.
Example:

```
python scraper.py --query "AI engineer Europe remote"
```

Another example:

```
python scraper.py --query "software engineer"
```

The query does not use advanced operators; it simply checks whether any of the terms appear in the job title, description, or location.

---

## Companies Included

Lever and Ashby no longer expose job data for many large companies. The script uses only organizations that still have active, public ATS endpoints.

**Lever:**

* sentry
* zapier
* remote
* retool
* clearbit
* pilot
* cerebras

**Ashby:**

* mistralai
* cohere
* runway
* adept
* instadeep
* character
* luma

These are chosen because they consistently return valid JSON job data and publish engineering/AI-focused roles.

---

## Output

Both CSVs use the same schema:

* `job_title`
* `company`
* `location`
* `description`
* `url`
* `id` (SHA-256 hash of the job URL)

`master_jobs.csv` grows over time.
`delta_jobs.csv` only contains the new jobs from the latest run.

If you want, I can rewrite this again in an even more minimal or more “junior developer” style — just tell me the tone you're aiming for.
