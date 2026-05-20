import math

from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, abort
from werkzeug.utils import secure_filename, safe_join
import os
from scrape_linkedin_jobs import scrape_linkedin_jobs
import json
from json.decoder import JSONDecodeError
import sqlite3
from datetime import datetime
import tempfile
import pypdf
from evaluate_jobs import summarize_resume, summarize_job, evaluate_job_fitness
from transformers import AutoTokenizer, AutoModelForCausalLM
from credentials import hf_token

UPLOAD_FOLDER = tempfile.gettempdir()
OUTPUT_FOLDER = "output"
ALLOWED_EXTENSIONS = {"json", "pdf"}

debug = False
use_llms = True
llm_name = "Qwen/Qwen2-1.5B-Instruct"

app = Flask(__name__, static_url_path="/static")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.secret_key = "abbbba"



def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=["GET", "POST"])
async def home():
    if request.method == "POST":
        # Try to make SQL database. If it exists, no problem.
        con = sqlite3.connect("jobs.db")
        cur = con.cursor()
        try:
            cur.execute("""CREATE TABLE jobs(
                            id integer PRIMARY KEY AUTOINCREMENT,
                            score integer,
                            date datetime,
                            company varchar,
                            title varchar,
                            url varchar,
                            details varchar,
                            description varchar,
                            analysis varchar,
                            logo varchar,
                            description_html varchar,
                            confidence_rating varchar,
                            job_summary varchar,
                        );""")
        except sqlite3.OperationalError:
            pass

        # Get the inputs from all the forms
        search = request.form.get("search-query")
        if search is None:
            search = ""
        job_location = request.form.get("job-location")
        if job_location is None:
            job_location = ""
        try:
            pages = float(request.form.get("page-count"))
        except TypeError:
            pages = 1
        try:
            job_time = request.form.get("job-time")
        except TypeError:
            job_time = "Anytime"
        try:
            salary = int(request.form.get("salary"))
        except TypeError:
            salary = "0"
        try:
            job_experience = request.form.getlist("job-experience")
        except TypeError:
            job_experience = []
        if 'Resume' not in request.files:
            print('No file part')
            return redirect(request.url)
        json_file = request.files['Json']
        resume_content = ""
        resume_summary = None
        custom_job_summarization_prompt = None
        custom_job_evaluation_prompt = None
        if json_file and allowed_file(json_file.filename):
            try:
                filename = secure_filename(json_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                json_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                json_file = open(filepath)
                json_dict = json.load(json_file)
                search = json_dict["search_query"]
                job_location = json_dict["job_location"]
                pages = float(json_dict["page_count"])
                salary = int(json_dict["salary"])
                job_time = json_dict["job_time"]
                job_experience = json_dict["job_experience"]
                resume_summary = json_dict["resume"]
                custom_job_summarization_prompt = json_dict["custom_job_summarization"]
                custom_job_evaluation_prompt = json_dict["custom_job_evaluation"]
            except ValueError:
                pass
        else:
            file = request.files['Resume']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                reader = pypdf.PdfReader(filepath)
                number_of_pages = len(reader.pages)
                for page_num in range(number_of_pages):
                    page = reader.pages[page_num]
                    resume_content += page.extract_text()

        print("Submitted things:")
        print(f"""
        search: {search}
        location: {job_location}
        resume: {resume_content}
        pages: {pages}
        job_time: {job_time}
        salary: {salary}
        job_experience: {job_experience}
               """)
        if not debug:
            jobs = await scrape_linkedin_jobs(search_query=search,
                                        pages=pages,
                                        date_filter=job_time,
                                        salary_filter=salary,
                                        experience_filter=job_experience,
                                        location=job_location)
            print("______________I finished scraping the jobs!____________________________")
            db_insert = []
            if use_llms:
                print("Starting up the LLMs...")
                tokenizer = AutoTokenizer.from_pretrained(llm_name, token=hf_token, device_map="auto")
                model = AutoModelForCausalLM.from_pretrained(llm_name, token=hf_token, device_map="auto")
            for job in jobs:
                # Ignore duped jobs
                check_dupes = cur.execute("SELECT * FROM JOBS WHERE (title = ? AND company = ?)",
                                          (job["title"], job["company"])).fetchall()
                if len(check_dupes) > 0:
                    continue
                job_evaluation = ""
                job_dict = {}
                if use_llms:
                    if resume_summary is None:
                        print("Summarizing Resume...")
                        resume_summary = summarize_resume(tokenizer, model, resume_content)
                        print("Resume summarized!")
                    print(f"Summarizing the job {job['title']} at {job['company']}")
                    job_summary = summarize_job(tokenizer, model, job["description"], custom_job_summarization_prompt)

                    print(f"Evaluating the job {job['title']} at {job['company']}")
                    job_evaluation = evaluate_job_fitness(tokenizer, model, resume_summary, job_summary, custom_job_evaluation_prompt)
                try:
                    job_dict["company"] = job["company"]
                    job_dict["title"] = job["title"]
                    job_dict["url"] = job["url"]
                    job_dict["details"] = job["details"]
                    job_dict["description"] = job["description"]
                    job_dict["description_html"] = job["description_html"]
                    job_dict["logo"] = job["logo"]
                    if use_llms:
                        job_dict["job_summary"] = job_summary
                        job_evaluation_json = json.loads(job_evaluation)
                        job_dict["analysis"] = job_evaluation_json["ANALYSIS"]
                        job_dict["confidence_rating"] = job_evaluation_json["CONFIDENCE"]
                    else:
                        job_dict["job_summary"] = "NA"
                        job_dict["analysis"] = "Not analyzed."
                        job_dict["confidence_rating"] = "UNKNOWN"

                except JSONDecodeError:
                    print("The model has output a malformed json. Attempting to fix this...")
                    job_dict["analysis"] = job_evaluation
                    if "HIGH" in job_evaluation:
                        job_dict["confidence_rating"] = "HIGH"
                    elif "MEDIUM" in job_evaluation:
                         job_dict["confidence_rating"] = "MEDIUM"
                    elif "LOW" in job_evaluation:
                         job_dict["confidence_rating"] = "LOW"
                    else:
                        job_dict["confidence_rating"] = "UNKNOWN"
                    print(job_evaluation)
                # Score parameter is just used to sort the jobs in order in the output page.
                if job_dict["confidence_rating"] == "HIGH":
                    job_dict["score"] = 100
                elif job_dict["confidence_rating"] == "MEDIUM":
                    job_dict["score"] = 50
                elif job_dict["confidence_rating"] == "LOW":
                    job_dict["score"] = 0
                else:
                    job_dict["score"] = 0
                db_insert.append((datetime.now(), job_dict["score"], job_dict["company"], job_dict["title"],
                    job_dict["url"], job_dict["details"], job_dict["description"],
                    job_dict["aalysis"],
                    job_dict["logo"], job_dict["description_html"], 
                    job_dict["confidence_rating"], job_dict["job_summary"]))
            cur.executemany(f""" INSERT INTO jobs (date, score, company, title, url, details, description, analysis, logo, description_html, confidence_rating, job_summary)
                        VALUES (?, /* date */
                                ?, /* score */
                                ?, /* company */
                                ?, /* title */
                                ?, /* url */
                                ?, /* details */
                                ?, /* description */
                                ?, /* analysis */
                                ?, /* logo */
                                ?, /* description_html */ 
                                ?, /* confidence_rating */
                                ?, /* job_summary */
                                );
                        """, db_insert)
            con.commit()
            con.close()
        else:
            print(f"""
                    search: {search}
                    resume: {resume_content}
                    pages: {pages}
                    job_time: {job_time}
                    salary: {salary}
                    job_experience: {job_experience}
                           """)
        return redirect(url_for("output"))
    return render_template("index.html")



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


    return render_template("output2.html", data=job_list, single_job=single_job)


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
    job_list = cur.execute(f"SELECT *, Date(date) as day FROM jobs ORDER BY day DESC, score DESC LIMIT 200 OFFSET ?", (offset,)).fetchall()
    cur.close()

    return render_template("summary.html", data=job_list, page=page, num_pages=num_pages)


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.run(host='0.0.0.0', port=5001)