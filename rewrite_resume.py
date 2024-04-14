from openai import OpenAI
from credentials import chatgpt_api, resume

client = OpenAI(api_key=chatgpt_api)


def rewrite_resume(job_description, resume):
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Replace with the correct model name
                                              messages=[
                                                  {"role": "user", "content": f"""
        I am trying to apply to a job. This is my resume: {resume}

        THIS IS THE JOB DESCRIPTION: {job_description}

        Please write an objective statement in my resume in order to make it more attractive to the hiring manager.
        Take into account the skills listed into my resume and how it ties into the job description.
        """
                                                   }
                                              ])
    print(response.choices[0].message.content)
    return response.choices[0].message.content


