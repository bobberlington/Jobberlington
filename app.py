from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, abort
from werkzeug.utils import secure_filename, safe_join
import os
from scrape_linkedin_jobs import scrape_linkedin_jobs
from evaluate_jobs import analyze_job_fit
import json
from json.decoder import JSONDecodeError
from credentials import resume
from config import search_query, linkedin_salary, linkedin_experience, linkedin_pages, linkedin_date, duplicate_job_threshold, max_jobs
from generate_htmltest import create_job_html

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
        search = request.form.get("search-query")
        if search == None:
            search = ""
        job_location = request.form.get("job-location")
        if job_location == None:
            job_location = ""
        resume = request.form.get("resume")
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
        print(f"""
        search: {search}
        resume: {resume}
        pages: {pages}
        job_time: {job_time}
        salary: {salary}
        job_experience: {job_experience}
               """)
        jobs = scrape_linkedin_jobs(search,
                                    pages=pages,
                                    date_filter=job_time,
                                    salary_filter=salary,
                                    experience_filter=job_experience,
                                    duplicate_job_threshold=duplicate_job_threshold,
                                    max_jobs=max_jobs,
                                    browser=browser,
                                    location=job_location)
        return f"""
        search: {search_query}
        resume: {resume}
        pages: {pages}
        job_time: {job_time}
        salary: {salary}
        job_experience: {job_experience}
               """
    return render_template("search_input.html")

"""
@app.route('/loanwithdrawal', methods=["GET", "POST"])
def loan_withdrawal_upload():
    # Upload a file.
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file1 = request.files['file1']
        file2 = request.files['file2']
        if file1.filename == '' or file2.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file1 and file2 and allowed_file(file1.filename) and allowed_file(file2.filename):
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            try:
                files = compare_jsons(os.path.join(app.config['UPLOAD_FOLDER'], filename1),
                                      (os.path.join(app.config['UPLOAD_FOLDER'], filename2)),
                                      os.path.join(app.config['UPLOAD_FOLDER'], filename1), 3,
                                      os.path.join("static", "loanwithdrawal"))
            except KeyError:
                abort(400)
            img = ""
            if len(files) == 2:
                img = files[0] + "%" + files[1]
            elif len(files) == 1:
                img = files[0]
            else:
                img = "none"
            try:
                files2 = compare_jsons(os.path.join(app.config['UPLOAD_FOLDER'], filename1),
                                       (os.path.join(app.config['UPLOAD_FOLDER'], filename2)), img, 2,
                                       os.path.join("static", "sharedexclusivejsons"))
                print(img)
                print(files2)
                f = open(f"static/sharedexclusivejsons/{files2}")
                output = json.dumps(f.read())
                f.close()
                print(output)
            except KeyError:
                abort(400)
            # Clear out uploads once we're done with them
            for i in os.listdir(app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i))

            return redirect(url_for('loan_withdrawal', name=img))
    return render_template("loan_withdrawal_upload.html")


@app.route('/loanwithdrawal/<name>', methods=["GET"])
def loan_withdrawal(name):
    # Outputs the graph of loans and withdrawals of 2 illutrations, and the
    # name is the filename(s) of the output
    f = open(safe_join("static/sharedexclusivejsons", name))
    json_dict = json.load(f)
    f.close()
    # Create the table for the shared and exclusive files.
    json_output_table = f"<table><tr><th>Policy Scalar</th><th>{json_dict['Scalars']['IllustrationID'][0]}</th><th>{json_dict['Scalars']['IllustrationID'][1]}</th><th>Difference</th></tr>"
    for key in json_dict["Scalars"].keys():
        if key == "IllustrationID":
            continue
        json_output_table += "<tr>"
        json_output_table += f"<td>{key}</td>"
        json_output_table += f"<td>{json_dict['Scalars'][key][0]}</td>"
        json_output_table += f"<td>{json_dict['Scalars'][key][1]}</td>"
        json_output_table += f"<td>{json_dict['Differences'][key]}</td>"
        json_output_table += "</tr>"
    json_output_table += "</table>"
    if "%" in name:
        return render_template("loan_withdrawal_output_2.html", graph1=f"loanwithdrawal/{name[0:name.index('%')]}",
                               graph2=f"loanwithdrawal/{name[name.index('%') + 1:]}", output=json_output_table)
    elif name != "none":
        return render_template("loan_withdrawal_output_1.html", graph=f"loanwithdrawal/{name}",
                               output=json_output_table)
    else:
        return render_template("loan_withdrawal_output_0.html", output=json_output_table)


@app.route('/policyvalues', methods=["GET", "POST"])
def policy_scalars_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                img = graph_json(os.path.join(app.config['UPLOAD_FOLDER'], filename), "static/policyvalues",
                                 request.form["xaxis"])
            except KeyError:
                abort(400)
            # Clear out uploads once we're done with them
            for i in os.listdir(app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i))
            return redirect(url_for('policy_scalars_output', name=img))
    return render_template("policy_values_upload.html")


@app.route('/policyvalues/<name>', methods=["GET"])
def policy_scalars_output(name):
    return render_template("policy_values_output.html", graph=f"policyvalues/{name}")


@app.route('/epfr', methods=["GET", "POST"])
def epfr_info_upload():
    if request.method == 'POST':
        if len(request.files.getlist("files")) == 0:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist("files")
        allowed = True
        for i in files:
            if not allowed_file(i.filename):
                allowed = False
                break
        if allowed:
            foldername = ""
            for i in range(len(files)):
                files[i].filename = secure_filename(files[i].filename)
                foldername += files[i].filename
            foldername = str(hash(foldername))
            temp = os.path.join(app.config["UPLOAD_FOLDER"], foldername)
            os.mkdir(temp)
            for i in files:
                i.save(os.path.join(temp, i.filename))
            illustrations = os.listdir(temp)
            epfr_info(illustrations, os.path.join("static", "epfr", f"{foldername}.json"), temp)
            # Clear out uploads once we're done with them
            for i in os.listdir(temp):
                os.remove(f"{temp}/{i}")
            os.rmdir(temp)
            return redirect(url_for('epfr_info_output', name=f"{foldername}.json"))
    return render_template("epfr.html")


@app.route('/epfr/<name>', methods=["GET"])
def epfr_info_output(name):
    f = open(safe_join("static/epfr", name))
    json_dict = json.load(f)
    f.close()
    # Create the table for the shared and exclusive files.
    json_output_table = f"<table><tr><th>IllustrationID</th><th>Product Name</th><th>Has EPFR?</th><th>Type</th></tr>"
    for i in range(len(json_dict["IllustrationID"])):
        json_output_table += "<tr>"
        json_output_table += f"<td>{json_dict['IllustrationID'][i]}</td>"
        json_output_table += f"<td>{json_dict['ProductName'][i]}</td>"
        json_output_table += f"<td>{json_dict['HasEPFR'][i]}</td>"
        json_output_table += f"<td>{json_dict['Type'][i]}</td>"
        json_output_table += "</tr>"
    json_output_table += "</table>"

    return render_template("epfr_output.html", output=json_output_table)
"""


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.run(host='0.0.0.0', port=5000)