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

UPLOAD_FOLDER = "tmp"
OUTPUT_FOLDER = "output"
ALLOWED_EXTENSIONS = {"json"}

app = Flask(__name__, static_url_path="/static")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.secret_key = "abbbba"


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Try to make SQL database. If it exists, no problem.
        con = sqlite3.connect("jobs.db")
        cur = con.cursor()
        try:
            cur.execute("""CREATE TABLE jobs(
                            id integer PRIMARY KEY AUTOINCREMENT,
                            date datetime,
                            score integer,
                            company varchar,
                            title varchar,
                            url varchar,
                            details varchar,
                            description varchar,
                            analysis varchar,
                            logo varchar,
                            description_html varchar,
                            relevant_field boolean,
                            relevant_skills boolean
                        );""")
        except sqlite3.OperationalError:
            pass

        # Try to detect browser of the user. Selenium will use the browser
        browser = request.headers.get('User-Agent')
        if "Firefox" in browser:
            browser = "firefox"
        elif "Chrome" in browser:
            browser = "chrome"
        elif "Safari" in browser:
            browser = "safari"
        elif "Edge" in browser:
            browser = "edge"
        else:
            browser = "other"
        print(browser)

        # Get the inputs from all the forms
        search = request.form.get("search-query")
        if search == None:
            search = ""
        job_location = request.form.get("job-location")
        if job_location == None:
            job_location = ""
        resume = request.form.get("resume")
        try:
            max_jobs = int(request.form.get("max-jobs"))
        except TypeError:
            max_jobs = 0

        excluded_words = request.form.get("blacklist")
        if excluded_words == None:
            excluded_words = []
        else:
            excluded_words = excluded_words.split(",")
            for i in range(len(excluded_words)):
                excluded_words[i] = excluded_words[i].strip()
        try:
            pages = int(request.form.get("page-count"))
        except TypeError:
            pages = 1
        try:
            job_time = int(request.form.get("job-time"))
        except TypeError:
            job_time = 0
        try:
            salary = int(request.form.get("salary"))
        except TypeError:
            salary = 0
        try:
            job_experience = request.form.getlist("job-experience")
        except TypeError:
            job_experience = []
        try:
            dupe_jobs = int(request.form.get("dupe-jobs"))
        except TypeError:
            dupe_jobs = 99999
        print(dupe_jobs)
        print(f"""
        search: {search}
        resume: {resume}
        pages: {pages}
        job_time: {job_time}
        salary: {salary}
        job_experience: {job_experience}
        max_jobs: {max_jobs}
               """)
        jobs = scrape_linkedin_jobs(search,
                                    pages=pages,
                                    date_filter=job_time,
                                    salary_filter=salary,
                                    experience_filter=job_experience,
                                    duplicate_job_threshold=dupe_jobs,
                                    max_jobs=max_jobs,
                                    browser=browser,
                                    location=job_location)
        print(jobs)
        # Send jobs into chatgpt, insert into database
        db_insert = []
        for job in jobs:
            # Ignore duped jobs
            check_dupes = cur.execute("SELECT * FROM JOBS WHERE (title = ? AND company = ?)",
                                      (job["title"], job["company"])).fetchall()
            if check_dupes is not None and dupe_jobs == 1:
                continue
            analysis = analyze_job_fit(job["description"], resume)
            print(job["company"])
            print(job["title"])
            try:
                job_dict = json.loads(analysis)

                if not job_dict["relevant_field"] or not job_dict["relevant_skills"]:
                    job_dict["confidence_rating"] = 0
                job_dict["company"] = job["company"]
                job_dict["title"] = job["title"]
                job_dict["url"] = job["url"]
                job_dict["details"] = job["details"]
                job_dict["description"] = job["description"]
                job_dict["description_html"] = job["description_html"]
                job_dict["logo"] = job["logo"]

                print(job_dict)

                db_insert.append((datetime.now(), job_dict["confidence_rating"], job_dict["company"], job_dict["title"],
                                  job_dict["url"], job_dict["details"], job_dict["description"],
                                  job_dict["requirements_analysis"], job_dict["relevant_field"],
                                  job_dict["relevant_skills"], job_dict["logo"], job_dict["description_html"]))

            except JSONDecodeError:
                print("Not a json! Maybe ChatGPT was acting up.")
                print(analysis)
        cur.executemany(f""" INSERT INTO jobs (date, score, company, title, url, details, description, analysis, relevant_field, relevant_skills, logo, description_html)
                    VALUES (?, 
                            ?,
                            ?,
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

        return redirect(url_for("output"))
    return render_template("search_input.html")

@app.route('/output', methods=["GET", "POST"])
def output():
    con = sqlite3.connect("jobs.db")
    method = "ADASD"

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    con.row_factory = dict_factory
    cur = con.cursor()
    if method == "score":
        job_list = cur.execute("SELECT * FROM jobs ORDER BY score DESC LIMIT 50").fetchall()
    elif method == "date":
        job_list = cur.execute("SELECT * FROM jobs ORDER BY date DESC LIMIT 50").fetchall()
    else:
        job_list = cur.execute("SELECT *, Date(date) as day FROM jobs ORDER BY day DESC, score DESC LIMIT 150").fetchall()


    return render_template("output.html", data=job_list)



if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.run(host='0.0.0.0', port=5000)