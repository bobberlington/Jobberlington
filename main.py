from scrape_linkedin_jobs import scrape_linkedin_jobs
from evaluate_jobs import analyze_job_fit
import json
from json.decoder import JSONDecodeError
from credentials import resume
from config import search_query, linkedin_salary, linkedin_experience, linkedin_pages, linkedin_date, duplicate_job_threshold, max_jobs, job_location
from generate_htmltest import create_job_html
import sqlite3
from datetime import datetime

jobs = scrape_linkedin_jobs(search_query,
                            pages=linkedin_pages,
                            date_filter=linkedin_date,
                            salary_filter=linkedin_salary,
                            experience_filter=linkedin_experience,
                            duplicate_job_threshold=duplicate_job_threshold,
                            max_jobs=max_jobs,
                            location=job_location)
print(jobs)
jobs_analysis = []
con = sqlite3.connect("jobs.db")
cur = con.cursor()
db_insert = []

for job in jobs:
    check_dupes = cur.execute("SELECT * FROM JOBS WHERE (title = ? AND company = ?)", (job["title"], job["company"])).fetchall()
    if check_dupes is not None and len(check_dupes) > duplicate_job_threshold:
        continue
    analysis = analyze_job_fit(job["description"], resume)
    print(job["company"])
    print(job["title"])
    try:
        job_dict = json.loads(analysis)

        if not job_dict["RelevantField"] or not job_dict["RelevantSkills"]:
            job_dict["ConfidenceRating"] = 0
        job_dict["Company"] = job["company"]
        job_dict["Title"] = job["title"]
        job_dict["Url"] = job["url"]
        job_dict["Details"] = job["details"]
        job_dict["Description"] = job["description"]
        job_dict["Description_Html"] = job["description_html"]
        job_dict["Logo"] = job["logo"]

        print(job_dict)
        jobs_analysis.append(job_dict)
        job_json = open(f"jobs/{job['company']}.json", "w")
        json.dump(job_dict, job_json)
        job_json.close()
        db_insert.append((datetime.now(), job_dict["ConfidenceRating"], job_dict["Company"], job_dict["Title"], job_dict["Url"], job_dict["Details"], job_dict["Description"], job_dict["RequirementsAnalysis"], job_dict["RelevantField"], job_dict["RelevantSkills"]))

    except JSONDecodeError:
        print("Not a json! Maybe ChatGPT was acting up.")
        print(analysis)
cur.executemany(f""" INSERT INTO jobs (date, score, company, title, url, details, description, analysis, relevant_field, relevant_skills)
        VALUES (?, 
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
                );
        """, db_insert)
con.commit()
create_job_html(jobs_analysis)

# TODO: Make html page grab from sql database
# Create pagination
# Make it sort by job score
# Implement Vagueness Score