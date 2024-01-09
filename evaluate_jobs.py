from openai import OpenAI
from credentials import chatgpt_api


client = OpenAI(api_key=chatgpt_api)


def analyze_job_fit(job_description, resume):

    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Replace with the correct model name
    messages=[
        {"role": "user", "content": f"""
        I am trying to apply to a job. This is my resume: {resume}
        
        THIS IS THE JOB DESCRIPTION: {job_description}
        
        Do you think this job is a good fit for me? What is your confidence that I would be able to get this job? Give your answer in JSON format, in which contains 2 fields:
        
        The first field is ConfidenceRating, a numerical value from 0-100 that is your percent in confidence that I would get the job. ConfidenceRating should be measured using a few different metrics:
        If the job description contains skills or experiences that my resume contains, this should reflect positively in the score and make it higher.
        However, if the job contains skills that I do not have in the resume, including ones that I may not have specific experience" in, this should cause the score to be penalized.
        If a job description contains both skills that are in the resume and skills that aren't in the resume, the score should be not be penalized.
        If the job description does not directly mention any skills that I have in my resume, the score should be 0.
        If the job description requires a degree in a discipline unrelated to my resume, the score should be 0.
        General non-specific "skills" shown through my previous experiences that don't relate to specific languages or frameworks should not be included as a positive point.
        If the job description asks for years of experience in a skill that I don't directly have written in the resume, the score should be 0.
        
        
        The other field is RequirementsAnalysis, a string value that holds your analysis of the requirements compared to my resume, acting as a reasoning for your ConfidenceRating.
        """
         }
    ])

    return response.choices[0].message.content

