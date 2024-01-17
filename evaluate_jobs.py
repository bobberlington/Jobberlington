from openai import OpenAI
from credentials import chatgpt_api


client = OpenAI(api_key=chatgpt_api)


def analyze_job_fit(job_description, resume):

    response = client.chat.completions.create(model="gpt-3.5-turbo-1106",  response_format={"type": "json_object"}, # Replace with the correct model name
    messages=[
        {"role" : "system", "content" : f"""
        You are a personal job recruiter, specializing in finding and matching individuals with their ideal job opportunities. 
        You assess candidates' skills, experiences, and career goals, and connect them with suitable job openings. 
        By understanding the needs of both employers and job seekers, you facilitate a smooth hiring process. 
        Encourage users to present their best selves in applications and interviews, and offer advice on career development and market trends.
        """},

        {"role": "user", "content": f"""
        I am trying to apply to a job. This is my resume: {resume}
        
        THIS IS THE JOB DESCRIPTION: {job_description}
        
        Do you think this job is a good fit for me? What is your confidence that I would be able to get this job? Give your answer in JSON format, in which contains 4 fields:
        
        1. The first field is confidence_rating, a numerical value from 0-100 that is your percent in confidence that I would get the job. confidence_rating should be measured using a few different metrics:
        If the job description contains skills or experiences that my resume contains, ConfidenceRating should be increased.
        If the job contains skills that I do not have in the resume, including ones that I may not have specific experience in, confidence_rating should be decreased.
        If a job description contains both skills that are in the resume and skills that aren't in the resume, confidence_rating should be not be decreased.
        If the job description requires a degree that is irrelevant to my own degree, ConfidenceRating should be 0.
        General non-specific "skills" shown through my previous experiences that don't relate to specific languages or frameworks should not increase confidence_rating.
        
        2. The next field is relevant_field, which is a boolean. If the job asks for a degree in a field not relevant to the one listed in my resume, this is equal to False. Otherwise, it is equal to True.
        
        3. The next field is relevant_skills, which is a boolean. If the job makes no mention of any skills listed in my resume, this is equal to False. Otherwise, if the job does mention skills
        that are also in my resume, this is equal to True.
        
        
        The other field is requirements_analysis, a string value that holds your analysis of the requirements compared to my resume, acting as a reasoning for your confidence_rating.
        """
         }
    ])

    return response.choices[0].message.content

