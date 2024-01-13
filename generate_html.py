import webbrowser
import time
import os
import random
from pathlib import Path
import sqlite3


def create_job_html(job_list):
    header = Path("templates/job_start.html").read_text()
    job_html = f"""
            {header}
    """
    count = 0

    con = sqlite3.connect("jobs.db")

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    con.row_factory = dict_factory
    cur = con.cursor()
    job_list = cur.execute("SELECT * FROM jobs ORDER BY score DESC LIMIT 50").fetchall()

    for job in job_list:
        if job["score"] >= 0 and job["score"] <= 70:
            score_class = "score-0"
        elif job["score"] > 70 and job["score"] <= 80:
            score_class = "score-1"
        else:
            score_class = "score-2"
        job_html += f"""
            <!-- Card feed item START -->
                <div class="card {score_class}">
					<!-- Card header START -->
					<div class="card-header border-0 pb-0">
						<div class="d-flex align-items-center justify-content-between">
							<div class="d-flex align-items-center">
								<!-- Avatar -->
								<div class="avatar  me-2">
									<a href="#!"> <img class="avatar-img" src="{job["logo"]}"  width=200px alt=""> </a>
								</div>
								<!-- Info -->
								<div>
									<div class="nav nav-divider">
										<h6 class="nav-item card-title mb-0"><a href="{job["url"]}">{job["title"]} at {job["company"]}</a></h6>
									</div>
									<p class="mb-0 small">{job["details"]}</p>
								</div>
							</div>

						</div>
					</div>
					<!-- Card header END -->
					<!-- Card body START -->
					<div class="card-body">
						<p>{job["description_html"]}</p>

						<!-- Card img -->
						<img class="card-img" src="" alt="">
						<!-- Feed react START -->
						<ul class="nav nav-stack py-3 small">

						</ul>
						<!-- Feed react END -->
                            <!-- Comment item START -->
                            <li class="comment-item" style="list-style: none;">
                                <div class="d-flex">
                                    <!-- Comment by -->

                                    <div class="ms-2">
                                        <div class="bg-light p-3 rounded">
                                            <div class="d-flex justify-content-between"> 
                                                <h6 class="mb-1"> <a href="#!"> Job Score </a> </h6>
                                            </div>
                                            <p class="small mb-0">{job["score"]}</p>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li class="comment-item" style="list-style: none;">
                                <div class="d-flex">
                                    <!-- Comment by -->

                                    <div class="ms-2">
                                        <div class="bg-light p-3 rounded">
                                            <div class="d-flex justify-content-between">
                                                <h6 class="mb-1"> <a href="#!"> Resume Analysis </a> </h6>
                                            </div>
                                            <p class="small mb-0">{job["analysis"]}</p>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <!-- Comment item END -->
								<!-- Comment item nested END -->
							</li>
							<!-- Comment item END -->

						</ul>
						<!-- Comment wrap END -->
					</div>
					<!-- Card body END -->
					<!-- Card footer START -->
					<div class="card-footer border-0 pt-0">

					</div>
					<!-- Card footer END -->
				</div>
				<!-- Card feed item END -->

        """
        count += 1
    ending = Path("templates/job_end.html").read_text()
    job_html += ending
    path = "temp.html"
    f = open(path, "w")
    f.write(job_html)
    f.close()
    webbrowser.open(f"file://{os.getcwd()}/{path}")
    time.sleep(1)
    os.remove(path)


if __name__ == "__main__":
    job_list = [
        {"Title": "Job",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": 50,
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "https://i.imgur.com/e60FoKF.png"
         },
        {"Title": "Job2",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": 60,
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
        {"Title": "Job3",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": 70,
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
        {"Title": "Job4",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": 80,
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
        {"Title": "Job5",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": 90,
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
        {"Title": "Job5",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": random.randint(50, 100),
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
        {"Title": "Job5",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": random.randint(50, 100),
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
        {"Title": "Job5",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": random.randint(50, 100),
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
        {"Title": "Job5",
         "Company": "Company",
         "Url": "http://www.youtube.com",
         "ConfidenceRating": random.randint(50, 100),
         "RequirementsAnalysis": "You will do this for sure",
         "Details": "9999 people applied at the Tack Zone",
         "Description_Html": "<p>Babababa</p>",
         "Logo": "<img src=https://i.imgur.com/e60FoKF.png width=400px>"
         },
    ]
    create_job_html(job_list)
