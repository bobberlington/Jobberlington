import math

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
                            relevant_skills boolean,
                            years_of_experience integer
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
            excluded_words = ""
        try:
            pages = int(request.form.get("page-count"))
        except TypeError:
            pages = 1
        try:
            years = int(request.form.get("years"))
        except TypeError:
            years = 0
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
                                    duplicate_job_threshold=1,
                                    max_jobs=max_jobs,
                                    browser=browser,
                                    location=job_location)
        print("______________I finished scraping the jobs!____________________________")
        # Send jobs into chatgpt, insert into database
        db_insert = []
        for job in jobs:
            # Ignore duped jobs
            check_dupes = cur.execute("SELECT * FROM JOBS WHERE (title = ? AND company = ?)",
                                      (job["title"], job["company"])).fetchall()
            if len(check_dupes) > 0:
                continue
            analysis = analyze_job_fit(job_description=job["description"], resume=resume, years=years, blacklist=excluded_words)
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
                if job_dict["years_of_experience"] > years:
                    penalty = (5 * (job_dict["years_of_experience"] - years))
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
        cur.executemany(f""" INSERT INTO jobs (date, score, company, title, url, details, description, analysis, relevant_field, logo, description_html, years_of_experience, confidence_value)
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
        cur.execute("INSERT into resume (date, resume) VALUES (?, ?)", (datetime.now(), resume))
        con.commit()
        con.close()

        return redirect(url_for("output"))
    return render_template("search_input.html")

@app.route('/output', methods=["GET", "POST"])
def output():
    try:
        id = request.args.get("id", None)
        print(id)
        if id is not None:
            id = int(id)
    except ValueError:
        return redirect(url_for("summary", page=1))

    if request.method == "POST":
        print(request.form.get("generate-resume"))
    con = sqlite3.connect("jobs.db")

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    con.row_factory = dict_factory
    cur = con.cursor()
    single_job = False
    if id is None:
        job_list = cur.execute("SELECT *, Date(date) as day FROM jobs ORDER BY day DESC, score DESC LIMIT 50").fetchall()
    else:
        job_list = cur.execute("SELECT *, Date(date) as day FROM jobs WHERE id = ? ORDER BY day DESC, score DESC LIMIT 1",(id,)).fetchall()
        single_job = True
    cur.close()


    return render_template("output.html", data=job_list, single_job=single_job)

@app.route('/generate_letter', methods=["GET", "POST"])
def cover_letter():
    try:
        id = request.args.get("id", None)
        if id == None:
            return redirect(url_for("error", error_type="job_id"))
        id = int(id)
    except ValueError:
        return redirect(url_for("error", error_type="job_id"))

    id = (id,)
    con = sqlite3.connect("jobs.db")
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    con.row_factory = dict_factory
    cur = con.cursor()
    job = cur.execute("SELECT * FROM jobs WHERE id = ?", id).fetchone()
    if job == None:
        cur.close()
        return redirect(url_for("error", error_type="job_id"))
    cover_letter = job["cover_letter"]
    objective = job["objective"]
    if cover_letter == None or objective == None:
        print("Didn't find a cover letter for this, making a new one")
        resume = cur.execute("SELECT resume FROM resume ORDER BY date DESC LIMIT 1 ").fetchone()
        if resume == None:
            cur.close()
            return redirect(url_for("error", error_type="resume"))
        cover_letter = write_cover_letter(job_description=job["description"], resume=resume)
        objective = rewrite_resume(job_description=job["description"], resume=resume)
        cur.execute("UPDATE jobs SET cover_letter = ?, objective = ? WHERE id = ?", (cover_letter, objective, id[0]))
        con.commit()
    cur.close()
    return render_template("output_cover_letter.html", job=job, cover_letter=cover_letter, objective=objective)


@app.route('/summary', methods=["GET", "POST"])
def summary():
    try:
        page = int(request.args.get("page", 1))
        offset = str((page - 1) * 50)
    except ValueError:
        return redirect(url_for("summary", page=1))
    con = sqlite3.connect("jobs.db")

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    con.row_factory = dict_factory
    cur = con.cursor()
    num_rows = cur.execute("SELECT COUNT(id) as row_count FROM jobs").fetchone()
    num_pages = math.ceil(num_rows["row_count"] / 50)
    job_list = cur.execute(f"SELECT *, Date(date) as day FROM jobs ORDER BY day DESC, score DESC LIMIT 50 OFFSET ?", (offset,)).fetchall()
    cur.close()

    return render_template("summary.html", data=job_list, page=page, num_pages=num_pages)
@app.route('/error')
def error():
    error_type = request.args.get("error_type", None)
    if error_type == "job_id":
        return render_template("error_job.html")
    elif error_type == "resume":
        return render_template("error_resume.html")
    else:
        return render_template("error_default.html")


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.run(host='0.0.0.0', port=5000)