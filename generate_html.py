import webbrowser
import time
import os

def create_job_html(job_list):
    job_html = """
    <html>
    """
    count = 0
    for job in job_list:
        if job["ConfidenceRating"] >= 0 and job["ConfidenceRating"] < 60:
            score_color = "#FF0000"
        elif job["ConfidenceRating"] >= 60 and job["ConfidenceRating"] < 70:
            score_color = "#FF6600"
        elif job["ConfidenceRating"] >= 70 and job["ConfidenceRating"] < 80:
            score_color = "#BBBB00"
        elif job["ConfidenceRating"] >= 80 and job["ConfidenceRating"] < 90:
            score_color = "#2E8200"
        else:
            score_color = "#00B38C"
        job_html += f"""
        <h2><a href={job["Url"]}>{job["Title"]} at {job["Company"]}</a></h2>
        <p>{job["Details"]}</p>
        <p style="color:{score_color}">Fitness Score: {job["ConfidenceRating"]}</p>
        {job["Description_Html"]}
        <p style="color:#1F1F1F"><i>{job["RequirementsAnalysis"]}</i></p>
        <input type="checkbox" id=job-{count}>
        <label for="job-{count}" style="color:#00559F">I would like to apply for this job.</label>
        """
        count += 1
    job_html += "</html>"
    path = "temp.html"
    f = open(path, "w")
    f.write(job_html)
    f.close()
    webbrowser.open(f"file://{os.getcwd()}/{path}")
    time.sleep(1)
    os.remove(path)

if __name__ == "__main__":
    job_list = [
        {"Title" : "Job",
         "Company" : "Company",
         "Url" : "http://www.youtube.com",
         "ConfidenceRating" : 90,
         "RequirementsAnalysis" : "Please die.",
         "Details" : "At San Jose"
         }]
    create_job_html(job_list)