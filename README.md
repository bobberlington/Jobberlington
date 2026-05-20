# Jobberlington

This is a tool that scrapes jobs from LinkedIn, then using your resume, feeds the jobs into an LLM, and determines which jobs are the best fit.

# How to Run
"credentials.py" requires you to put your linkedin email and password, and huggingface token hf_token as strings. This is required.

While it is not required, putting in a resume called "resume.pdf" into the same folder and running the "create_jobberlington_json.ipynb" file will pre-generate a json file for you with all the configuration options which you can upload directly to the flask app and skip having to type in everything. You can make it summarize your resume for you immediately which is more efficient than having to do it potentially every time you scrape.

Actually running the tool starts with running app.py and going to your localhost, where it runs the Flask app. Here, you type in your info (or just upload the json which does the same thing but faster) and click submit at which point the scraping should begin.

After you begin scraping, it should open a Chrome window and begin working. the first time you run it it will automatically type in your email and password for you, and then it will wait 30 seconds doing nothing to give you time to type in a code if it asks you to verify by sending you a code through your email. Afterwards, it will save your cookies in a file which will prevent this from happening again.

After it's done scraping, the LLM turns on and starts doing the evaluation, at which point you can just wait for it to complete.