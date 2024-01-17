from openai import OpenAI
from credentials import chatgpt_api, resume
import sqlite3


client = OpenAI(api_key=chatgpt_api)


def write_cover_letter(job_description, resume):

    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Replace with the correct model name
    messages=[
        {"role": "user", "content": f"""
        I am trying to apply to a job. This is my resume: {resume}
        
        THIS IS THE JOB DESCRIPTION: {job_description}
        
        Please write a cover letter to the hiring manager of this job showing my enthusiasm for the job. 
        This letter should use the skills listed in my resume to establish how I am a good fit for the job. It should be
        in a conversational tone and be in 150 words or less.
        """
         }
    ])

    return response.choices[0].message.content

con = sqlite3.connect("jobs.db")
cur = con.cursor()
cur.execute("""SELECT description FROM jobs WHERE company="ICW Group" """)


job_desc = cur.fetchone()

print(write_cover_letter(job_desc, resume))

