from openai import OpenAI
from credentials import chatgpt_api, resume

client = OpenAI(api_key=chatgpt_api)


def write_cover_letter(job_description, resume):
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

    return response.choices[0].message.content


job_desc = """
"About the job\nJob Summary: As a Rackspace Cloud Engineer III you\u2019llImplement cloud strategy from a technical perspective, including design, planning, integration, maintenance, and support of cloud architecture. Supports development and execution of cloud implementation strategy within organization's existing IT infrastructure. Work with stakeholders across organization to evaluate cloud systems and identify appropriate solutions. Responsible for adhering to company security policies and procedures and any other relevant policies and standards as directed.\n\nWork Location:  Remote\n\nKey Responsibilities\n\nCreate well-designed, documented, and tested software features that meet customer requirements.\nIdentify and address product bugs, deficiencies, and performance bottlenecks.\nWork with customers engineering teams on a wide variety of projects.\nWrite infrastructure as code (CloudFormation, Terraform).\nImplement automation/DevOps best practices for CI/CD, IaC, Containerization, etc.\nPerform Linux/Windows administration, automated deployments, scripting (Bash/PowerShell/Python).\nCollaborate with fellow Rackers and customer key stakeholders to deliver projects, such as implementing Cloud-based technical architectures, executing migrations, and optimizing applications that enable business objectives.\nServe as a technical advisor and perform troubleshooting to resolve technical challenges for customers.\n\nQualifications\n\nBachelor's Degree in field related to role preferred. High School Diploma is required.\nMin 5 yrs of progressive AWS cloud engineering. \nExpert level knowledge of AWS. \nExperience with Serverless Frameworks for AWS. \nStorage experience including Object Storage. \nExperience with CloudFormation and Terraform. \nWorking knowledge of Systems Manager Suite.\nExpert scripting skills especially with Python. \nExperience using Jinja2 for templating.\nExpert level knowledge of GitLab CI/CD.\nDeep level understanding of cloud and hybrid networking.\n\nDiscover your inner Racker:  Racker Life\n\nThe following information is required by pay transparency legislation in the following states: CA, CO, HI, NY, and WA. This information applies only to individuals working in these states.\n\nThe anticipated starting pay range for Colorado is: $105,100 - $154,110.\nThe anticipated starting pay range for the states of Hawaii and New York (not including NYC) is: $111,800 - $164,010.\nThe anticipated starting pay range for California, New York City and Washington is: $122,500 - $179,630.\n\nUnless already included in the posted pay range and based on eligibility, the role may include variable compensation in the form of bonus, commissions, or other discretionary payments. These discretionary payments are based on company and/or individual performance and may change at any time. Actual compensation is influenced by a wide array of factors including but not limited to skill set, level of experience, licenses and certifications, and specific work location. Information on benefits offered is here .\n\nAbout Rackspace Technology\n\nWe are the multicloud solutions experts. We combine our expertise with the world\u2019s leading technologies \u2014 across applications, data and security \u2014 to deliver end-to-end solutions. We have a proven record of advising customers based on their business challenges, designing solutions that scale, building and managing those solutions, and optimizing returns into the future. Named a best place to work, year after year according to Fortune, Forbes and Glassdoor, we attract and develop world-class talent. Join us on our mission to embrace technology, empower customers and deliver the future.\n\nMore on Rackspace Technology\n\nThough we\u2019re all different, Rackers thrive through our connection to a central goal: to be a valued member of a winning team on an inspiring mission. We bring our whole selves to work every day. And we embrace the notion that unique perspectives fuel innovation and enable us to best serve our customers and communities around the globe. We welcome you to apply today and want you to know that we are committed to offering equal employment opportunity without regard to age, color, disability, gender reassignment or identity or expression, genetic information, marital or civil partner status, pregnancy or maternity status, military or veteran status, nationality, ethnic or national origin, race, religion or belief, sexual orientation, or any legally protected characteristic. If you have a disability or special need that requires accommodation, please let us know.",

"""

print(write_cover_letter(job_desc, resume))

