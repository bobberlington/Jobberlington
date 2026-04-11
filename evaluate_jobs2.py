from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from anthropic.types import Message
from datetime import datetime
from anthropic.types import ToolParam

client = Anthropic()
model = "claude-sonnet-4-0"
system = """
You are a personal job recruiter, specializing in finding and matching individuals with their ideal job opportunities. 
You assess candidates' skills, experiences, and career goals, and connect them with suitable job openings. 
By understanding the needs of both employers and job seekers, you facilitate a smooth hiring process. 
Encourage users to present their best selves in applications and interviews, and offer advice on career development and market trends.
        """



def analyze_job_fit(job_description, resume, years=0, blacklist=[]):
    messages = []
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": 1.0,
        "system" : system,
    }
    prompt = f"""
    You are helping me to review the prospect of a job posting. Here my resume: 
    
        <my_resume>
            {resume}
        </my_resume>
        
        
        THIS IS THE JOB DESCRIPTION: 
        <job_description>
            {job_description}
        </job_description>

        <job_score_requirements>
        
            Based on your experience as an expert job recruiter, review the job description in the posting and compare them to my work experience and technical skills and provide feedback. Your assessments should come from the hiring manager’s perspective, the answers should be objective, stringent, and do not make assumptions on my potential when the job requirements & experience levels do not match my existing experience verbatim.  Give your answers in JSON format, in which contains 4 fields and the questions are  described below:
    
            {{
            confidence_rating: "YOUR ANSWER HERE",  // a ENUM value
            requirements_analysis: "",
            relevant_field: "",
            years_of_experience: "",
            has_degree: [],
            }}
                    
            Here are the meanings of each field: 
            
            <confidence_rating_explanation>
                confidence_rating : 
                This is a ENUM field with 3 possible values:  HIGH, MEDIUM, LOW. 
                Which indicates, from the hiring manager’s perspective, how attractive my profile is based on the requirements.
                When evaluating this, find the requirements that are most relevant to the job's title and weight the highest.
                Degree requirements, work experience, or knowledge of specific standards are often most important, and they also tend to be the first few requirements on the list.
                
                For example:
                <confidence_rating_example>
                    If a job description says this:
                    <example_job_description>
                        Product Review Engineer II
                    
                        Bachelor’s degree in Mechanical Engineering or related field or combination of similar education and work-related experience.
                        · Minimum of 3-5 years relevant work experience in Engineering field required, preference for work experience in product testing/compliance, regulatory, codes and standards, or related field.
                        · Working knowledge of both USA and Canadian product performance standards. 
                        · Excellent written and oral communication skills. 
                        · Computer literacy sufficient to operate spreadsheet and word processing applications (i.e., Microsoft Excel, Microsoft Word, Microsoft PowerPoint).
                        · Ability to maintain a consistent degree of importance, strong organizational skills, and attention to detail with the ability to manage multiple priorities to complete tasks within established, and often, tight, timelines. 
                        · Excellent skills in team collaboration and communication.
                    </example_job_description>
                    
                    My resume needs contain experience in mechanical engineering or construction. 
                    The most relevant skills in this job relate to mechanical engineering, so it should be given the most weight.
                    Written and oral skills and computer literacy are far less relevant and specific to the job at hand, it should not weighted highly in the final evaluation.
                    
                    
                </confidence_rating_example>
            
            </confidence_rating_explanation>
            
            <requirements_analysis_explanation>
                The next field is requirements_analysis, a string value that holds your analysis of the requirements compared to my resume. 
                Explain why you arrived at the final result.
            </requirements_analysis_explanation>
            
            <relevant_field_explanations>
                The next field is relevant_field, which is a string. 
                Search for the academic degree that the job asks for. 
                Then search for the degree in my resume. 
                If they are in unrelated fields, label “different”. 
                If the job’s degree is a higher degree than mine (for example, if the job asks for a Master’s or PHD while my resume has a Bachelor’s), label as “different”. 
                If the job asks for a degree that is the same as my resume, label it as “same”. 
                If the job description asks for a degree that is in a field closely related to the one in my resume, label as “similar”.  
                If you cannot find the degree level, label as "none". If you cannot find the major that the degree is in, label as "none".
                
                <relevant_field_example>
                    For example, if the job requires a Bachelor's in Mechanical Engineering, 
                    and my resume says I have a Bachelor's in Data Science, 
                    label it "different", because those degrees are not related.
                </relevant_field_example>
                <relevant_field_example>
                    If the job requires a Bachelor's in Computer Science, 
                    and my resume says I have a Bachelor's in Data Science, 
                    label it "similar", because those degrees are related.
                </relevant_field_example>
                <relevant_field_example>
                    If the job requires a Master's in Computer Science, 
                    and my resume says I have a Bachelor's in Data Science, 
                    label it "different", because I have a Bachelor's, which is under a Master's.
                </relevant_field_example>
                
            </relevant_field_explanations>
            
            
        </job_score_requirements>
        
         
    """

    messages.append(prompt)
    message = client.messages.create(**params)
    return message
    return