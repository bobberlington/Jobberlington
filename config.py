# Job title to search
search_query = "Software Engineer"

# Number of pages to search in LinkedIn.
linkedin_pages = 5

# Which date range to search in
# 1: Searches for jobs in the "past month"
# 2: Searches for jobs in the "past week"
# 3: Searches for jobs in the "past 24 hours"
# Defaults to "any time" otherwise
linkedin_date = 2

# Experience levels to search for in Linkedin.
# 1 - Whether to search "Internship" or not
# 2 - Whether to search "Entry level" or not
# 3 - Whether to search "Associate" or not
# 4 - Whether to search "Mid-Senior level" or not
# 5 - Whether to search "Director" or not
# 6 - Whether to search "Executive" or not

linkedin_experience = [2]

# Which salary range to search for in LinkedIn.
# 1: Searches for jobs with salary $40k+
# 2: Searches for jobs with salary $60k+
# 3: Searches for jobs with salary $80k+
# 4: Searches for jobs with salary $100k+
# 5: Searches for jobs with salary $120k+
# 6: Searches for jobs with salary $140k+
# 7: Searches for jobs with salary $160k+
# 8: Searches for jobs with salary $180k+
# 9: Searches for jobs with salary $200k+
# Defaults to searching for everything otherwise

linkedin_salary = 3

# If jobs from the same company are found this number of times, further jobs are ignored.
duplicate_job_threshold = 1

# Max number of jobs that are pulled. -1 means it goes until we reach the number of pages.
max_jobs = -1

# Location to search jobs in
job_location = "California, United States"
