from openai import OpenAI

import credentials
from credentials import chatgpt_api, resume



client = OpenAI(api_key=chatgpt_api)


def analyze_job_fit(job_title, job_description, resume, years=0, blacklist=[]):

    response = client.chat.completions.create(model="gpt-5-mini",  response_format={"type": "json_object"}, # Replace with the correct model name
    messages=[
        {"role" : "system", "content" : f"""
        You are a personal job recruiter, specializing in finding and matching individuals with their ideal job opportunities. 
        You assess candidates' skills, experiences, and career goals, and connect them with suitable job openings. 
        By understanding the needs of both employers and job seekers, you facilitate a smooth hiring process. 
        Encourage users to present their best selves in applications and interviews, and offer advice on career development and market trends.
        """},

        {"role": "user", "content": f"""
   You are helping me to review the prospect of a job posting. Here my resume: 
    
        <my_resume>
            {resume}
        </my_resume>
        
        
        The job title is this:

        <job_title>
            {job_title}
        </job_title>
        and the job description is:
        <job_description>
            {job_description}
        </job_description>

        <job_score_requirements>
        
            Based on your experience as an expert job recruiter, review the job description in the posting and compare them to my work experience and technical skills and provide feedback. Your assessments should come from the hiring manager’s perspective, but also reflect how recruiters realistically weigh transferable skills and related experience. The answers should be objective and evidence-based, but do not automatically penalize small gaps if the resume shows strong alignment overall. Give your answers in JSON format, which contains 3 fields described below:    
            {{
            confidence_rating: "YOUR ANSWER HERE",  // a ENUM value
            requirements_analysis: "",
            relevant_field: "",
            }}
                    
            Here are the meanings of each field: 
            
            <confidence_rating_explanation>
                confidence_rating : 
                This is a ENUM field with 3 possible values:  HIGH, MEDIUM, LOW. 
                    This is a ENUM field with 3 possible values: HIGH, MEDIUM, LOW. 
                    Which indicates, from the hiring manager’s perspective, how attractive my profile is based on the requirements.
                    When evaluating this, give the most weight to degree requirements, work experience level, and domain-specific expertise. Secondary requirements (such as tools, frameworks, or soft skills) should not outweigh strong alignment with the core requirements.                
                    
                     
                Ratings should follow these rules:
                - HIGH: Resume matches most or all critical requirements (degree, experience level, domain-specific skills). Minor gaps in secondary requirements do not prevent a HIGH rating if transferable skills or closely related experience are demonstrated.
                - MEDIUM: Resume meets some critical requirements but has notable gaps in degree, years of experience, or specialized domain knowledge. Strong transferable skills may raise a LOW to MEDIUM, but not MEDIUM to HIGH.
                - LOW: Resume does not meet most of the critical requirements or lacks alignment in degree, field, and experience level.

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
                If the job's degree is a higher degree than mine (for example, if the job asks for a Master’s or PHD while my resume has a Bachelor’s), label as “different”. 
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
        
        Only output valid JSON, and do not write any additional text. Do not embed the json in any format such as ```json."""

         }
    ])

    return response.choices[0].message.content

if __name__ == "__main__":
    job = """
     About the job
Responsibilities
Founded in 2012, ByteDance's mission is to inspire creativity and enrich life. With a suite of more than a dozen products, including TikTok, Helo, and Resso, as well as platforms specific to the China market, including Toutiao, Douyin, and Xigua, ByteDance has made it easier and more fun for people to connect with, consume, and create content.
Why Join Us
Creation is the core of ByteDance's purpose. Our products are built to help imaginations thrive. This is doubly true of the teams that make our innovations possible.
Together, we inspire creativity and enrich life - a mission we aim towards achieving every day.
To us, every challenge, no matter how ambiguous, is an opportunity; to learn, to innovate, and to grow as one team. Status quo? Never. Courage? Always.
At ByteDance, we create together and grow together. That's how we drive impact - for ourselves, our company, and the users we serve.
Join us.
About The Team:
The Applied Machine Learning Enterprise team combines system engineering and machine learning to develop and operate big model service platform that offers businesses Model-as-a-Service solutions (MaaS) to both the big model vendors and users. We are actively seeking talented Software Engineers/Researchers specializing in Large Language Models (LLM) to join our dynamic team.
We are looking for talented individuals to join our team in 2024. As a graduate, you will get unparalleled opportunities for you to kickstart your career, pursue bold ideas and explore limitless growth opportunities. Co-create a future driven by your inspiration with ByteDance.
Successful candidates must be able to commit to one of the following start dates below:

    January 15, 2024
    February 5, 2024
    March 4, 2024
    May 20, 2024
    June 10, 2024
    July 15, 2024
    August 12, 2024


We will prioritize candidates who are able to commit to these start dates. Please state your availability and graduation date clearly in your resume.
Applications will be reviewed on a rolling basis. We encourage you to apply early.
Candidates can apply for a maximum of TWO positions and will be considered for jobs in the order you applied for. The application limit is applicable to ByteDance and its affiliates' jobs globally.
Responsibilities:
In this role, you will be at the forefront of cutting-edge research and development of advanced techniques for MaaS solutions including model continuous pretraining, fine-tuning, evaluation, inference capabilities and also LLM application/agent development. Your primary responsibility will be to: lead the creation of next-generation, high-capacity LLM platforms and innovative products.
    work closely with cross-functional teams to plan and implement projects harnessing LLMs for diverse purposes and vertical domains.
    Maintain a deep passion for contributing to the success of large models is essential in this innovative and fast-paced team environment.


Qualifications
Qualifications:
    Ph.D./Master in Computer Science, Artificial Intelligence, or a related field.
    Have prior experience working with training and inference of large language models.
    Strong understanding of cutting-edge LLM research (e.g., long context, multi modality, alignment research etc.) and possess practical expertise in effectively implementing these advanced systems.
    Proficiency in programming languages such as Python or C++ and a track record of working with deep learning frameworks (e.g., pytorch, deepspeed, etc.).
    Strong understanding of distributed computing framework & performance tuning and verification for training/finetuning/inference. Being familiar with PEFT or MoE is a plus.
Preferred Qualifications:
    Excellent problem-solving skills and a creative mindset to address complex AI challenges. Demonstrated ability to drive research projects from idea to implementation, producing tangible outcomes.
    Published research papers or contributions to the LLM community would be a significant plus.
    Experience with inference tuning and Inference acceleration. Have a deep understanding of GPU and/or other AI accelerators, experience with large scale AI networks, pytorch 2.0 and similar technologies.
    Experience with large scale machine learning systems' scheduling and orchestration, familiar with Kubernetes and Cloud Native technologies.
    Experience with deploying AI models into production environments, testing and evaluation of AI systems, LLM application & agent development is desirable.
ByteDance is committed to creating an inclusive space where employees are valued for their skills, experiences, and unique perspectives. Our platform connects people from across the globe and so does our workplace. At ByteDance, our mission is to inspire creativity and enrich life. To achieve that goal, we are committed to celebrating our diverse voices and to creating an environment that reflects the many communities we reach. We are passionate about this and hope you are too.
ByteDance Inc. is committed to providing reasonable accommodations in our recruitment processes for candidates with disabilities, pregnancy, sincerely held religious beliefs or other reasons protected by applicable laws. If you need assistance or a reasonable accommodation, please reach out to us at earlycareers.accommodations@bytedance.com.
By submitting an application for this role, you accept and agree to our global applicant privacy policy, which may be accessed here: https://jobs.bytedance.com/en/legal/privacy.
Job Information:
【For Pay Transparency】Compensation Description (annually)
The base salary range for this position in the selected city is $112200 - $147000 annually.
Compensation may vary outside of this range depending on a number of factors, including a candidate’s qualifications, skills, competencies and experience, and location. Base pay is one part of the Total Package that is provided to compensate and recognize employees for their work, and this role may be eligible for additional discretionary bonuses/incentives, and restricted stock units.
Our Company Benefits Are Designed To Convey Company Culture And Values, To Create An Efficient And Inspiring Work Environment, And To Support Our Employees To Give Their Best In Both Work And Life. We Offer The Following Benefits To Eligible Employees:
We cover 100% premium coverage for employee medical insurance, approximately 75% premium coverage for dependents and offer a Health Savings Account(HSA) with a company match. As well as Dental, Vision, Short/Long term Disability, Basic Life, Voluntary Life and AD&D insurance plans. In addition to Flexible Spending Account(FSA) Options like Health Care, Limited Purpose and Dependent Care.
Our time off and leave plans are: 10 paid holidays per year plus 17 days of Paid Personal Time Off (PPTO) (prorated upon hire and increased by tenure) and 10 paid sick days per year as well as 12 weeks of paid Parental leave and 8 weeks of paid Supplemental Disability.
We also provide generous benefits like mental and emotional health benefits through our EAP and Lyra. A 401K company match, gym and cellphone service reimbursements. The Company reserves the right to modify or change these benefits programs at any time, with or without notice. 
    """
    job_test = analyze_job_fit(job_description=job, resume=credentials.resume, years=4)
    test_file = open("job_test.txt", "w")
    test_file.write(job_test)
    test_file.close()


