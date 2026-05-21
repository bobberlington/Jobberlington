# Jobberlington

This is a tool that scrapes jobs from LinkedIn, then using your resume, feeds the jobs into an LLM, and determines which jobs are the best fit.

# How to Run
"credentials.py" requires you to put your linkedin email and password, and huggingface token hf_token as strings. This is required.

While it is not required, putting in a resume called "resume.pdf" into the same folder and running the "create_jobberlington_json.ipynb" file will pre-generate a json file for you with all the configuration options which you can upload directly to the flask app and skip having to type in everything. You can make it summarize your resume for you immediately which is more efficient than having to do it potentially every time you scrape.

Actually running the tool starts with running app.py and going to your localhost, where it runs the Flask app. Here, you type in your info (or just upload the json which does the same thing but faster) and click submit at which point the scraping should begin.

After you begin scraping, it should open a Chrome window and begin working. the first time you run it it will automatically type in your email and password for you, and then it will wait 30 seconds doing nothing to give you time to type in a code if it asks you to verify by sending you a code through your email. Afterwards, it will save your cookies in a file which will prevent this from happening again.

After it's done scraping, the LLM turns on and starts doing the evaluation, at which point you can just wait for it to complete.

By default, the queries are simple.

Resume summarization:
- I will send my resume. Summarize the skills demonstrated in my experiences and output it in a list in bullet point format. On the first line, put a bullet for my educational status.

Job Summarization:
- I will send a job description. Summarize the required skills in the description.

Job fitness evaluation:
- Would I be able to apply to this job? 
        Structure the output in json format, with 2 fields: 
        The first field is ANALYSIS: Do a 4 sentence analysis by seeing if my resume's skills match well to the job's skills. 
        The second field is CONFIDENCE: A single word: Answer 'HIGH' if the skills match well, 'MEDIUM' if only some skills match well, or 'LOW' if only a few skills are relevant. 
        Additionally, if the job asks for a degree greater than the one in my resume, answer LOW. 
        AFTER COMPLETING THE JSON, DO NOT WRITE ANYTHING ELSE.

It is possible to configure these prompts to be different, although with the main constraint that the final evaluation prompt is very much expected to have the output in json format, with the two specific fields. Here are some examples of other prompts you could configure, though. This means you could focus your output on specific things if you wanted jobs with specific features.

### Resume summarization examples:

Summarize the skills demonstrated in my resume, being sure to not miss my focus on my leadership abilities.

Put additional focus on my internship working at Company...

...Ignore my objective statement...

...Do not mention my experience working at Company...

...Keep the summarization short, only up to 10 lines, mostly focusing on X and Y.

(Additionally, you are given this summarization inside of jobberlington.json, and therefore you can edit it manually afterwards.)


### Job summarization examples:

...Additionally, list the medical benefits of the job, such as dental insurance.

...List if the job requires you to be an enrolled student.

...List if the job is contract work.

...List if the job requires any form of certification

...List how many years of experience the job asks for.

...List the number of hours per week in the job.

...List if the job is remote, in person, or hybrid.

### Job evaluation examples:

...If the job asks for experience in cloud platforms, answer 'LOW' confidence.

...If the job mentions a temporary period of employment, answer 'LOW' confidence.

...The first field is ANALYSIS: Simply have this as an empty string. (If you wanted to save on tokens... but typically I find making the LLM reason is a good idea)

...If the job asks for experience in python, answer 'HIGH' confidence.

...I have only 1 year of experience. If the job asks for 5 years of experience, decrease confidence.

...If the job is at the company Q, answer 'LOW' confidence.

...If the job does not have insurance benefits, answer 'LOW' confidence.

...If the company is listed as a startup, increase the confidence.

...If the job is not remote, answer 'LOW' confidence.

...If the job talks about using AI-assisted coding, decrease the confidence.




