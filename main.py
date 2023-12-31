from scrape_linkedin_jobs import scrape_linkedin_jobs
from evaluate_jobs import analyze_job_fit
import json
from json.decoder import JSONDecodeError
from credentials import resume
from config import search_query, linkedin_salary, linkedin_experience, linkedin_pages, linkedin_date, duplicate_job_threshold, max_jobs
from generate_html import create_job_html

jobs = scrape_linkedin_jobs(search_query,
                            pages=linkedin_pages,
                            date_filter=linkedin_date,
                            salary_filter=linkedin_salary,
                            experience_filter=linkedin_experience,
                            duplicate_job_threshold=duplicate_job_threshold,
                            max_jobs=max_jobs)
print(jobs)
jobs_analysis = []

for job in jobs:
    analysis = analyze_job_fit(job["description"], resume)
    print(job["company"])
    print(job["title"])
    try:
        job_dict = json.loads(analysis)
        job_dict["Company"] = job["company"]
        job_dict["Title"] = job["title"]
        job_dict["Url"] = job["url"]
        job_dict["Details"] = job["details"]
        job_dict["Description"] = job["description"]
        job_dict["Description_Html"] = job["description_html"]

        print(job_dict)
        jobs_analysis.append(job_dict)
        job_json = open(f"jobs/{job['company']}.json", "w")
        json.dump(job_dict, job_json)
        job_json.close()
    except JSONDecodeError:
        print("Not a json! Maybe ChatGPT was acting up.")
        print(analysis)
create_job_html(jobs_analysis)
