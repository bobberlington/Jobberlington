from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, abort
from werkzeug.utils import secure_filename, safe_join
import os
from scrape_linkedin_jobs import scrape_linkedin_jobs
from evaluate_jobs import analyze_job_fit
import json
from json.decoder import JSONDecodeError
from credentials import resume
from generate_htmltest import create_job_html
import sqlite3
from datetime import datetime
from cover_letter import write_cover_letter
from rewrite_resume import rewrite_resume

con = sqlite3.connect("jobs.db")

years = 4


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


con.row_factory = dict_factory
cur = con.cursor()
jobs = cur.execute("SELECT * FROM jobs WHERE id > 133 and id < 202").fetchall()
my_resume = cur.execute("SELECT * FROM resume").fetchone()["resume"]
db_insert = []
my_years = 4

for job in jobs:
    analysis = analyze_job_fit(job_description=job["description"], resume=resume, years=years)
    print(job["company"])
    print(job["title"])
    try:
        job_dict = json.loads(analysis)
        score = 0
        if job_dict["confidence_rating"] == "HIGH":
            score = 80
        elif job_dict["confidence_rating"] == "MEDIUM":
            score = 60
        elif job_dict["confidence_rating"] == "LOW":
            score = 30

        if job_dict["relevant_field"] == "same":
            score += 5
        elif job_dict["relevant_field"] == "different":
            score -= 10
        if job_dict["years_of_experience"] > my_years:
            penalty = (5 * (job_dict["years_of_experience"] - my_years))
            if penalty > 20:
                penalty = 20
            score -= penalty
            if score < 0:
                score = 0
        job_dict["score"] = score
        job_dict["company"] = job["company"]
        job_dict["title"] = job["title"]
        job_dict["url"] = job["url"]
        job_dict["details"] = job["details"]
        job_dict["description"] = job["description"]
        job_dict["description_html"] = job["description_html"]
        job_dict["logo"] = job["logo"]

        print(job_dict)

        db_insert.append((datetime.now(), job_dict["score"], job_dict["company"], job_dict["title"],
                          job_dict["url"], job_dict["details"], job_dict["description"],
                          job_dict["requirements_analysis"], job_dict["relevant_field"],
                          job_dict["logo"], job_dict["description_html"], job_dict["years_of_experience"],
                          job_dict["confidence_rating"]))

    except JSONDecodeError:
        print("Not a json! Maybe ChatGPT was acting up.")
        print(analysis)
cur.executemany(f""" INSERT INTO jobs2 (date, score, company, title, url, details, description, analysis, relevant_field, logo, description_html, years_of_experience, confidence_value)
            VALUES (?, /* date */
                    ?, /* score */
                    ?, /* company */
                    ?, /* title */
                    ?, /* url */
                    ?, /* details */
                    ?, /* description */
                    ?, /* analysis */
                    ?, /* relevant_field */
                    ?, /* logo */
                    ?, /* description_html */ 
                    ?, /* years_of_experience */
                    ?  /* confidence_value */
                    );
            """, db_insert)
con.commit()
con.close()
