from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from credentials import email_login, linkedin_password, gmail_password
import imaplib
import email
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from selenium.common.exceptions import NoSuchElementException
import pickle

def get_gmail_credentials():
    SCOPES = ['https://mail.google.com/']
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

"""
Search through linkedin jobs.


search_query: The search query

pages: The pages to look for

date_filter: An int with the values values:
1: Searches for jobs in the "past month"
2: Searches for jobs in the "past week"
3: Searches for jobs in the "past 24 hours"
Defaults to "any time" otherwise

experience_filter: list with the values:
[
1 - Whether to search "Internship" or not
2 - Whether to search "Entry level" or not
3 - Whether to search "Associate" or not
4 - Whether to search "Mid-Senior level" or not
5 - Whether to search "Director" or not
6 - Whether to search "Executive" or not
]
Defaults to searching everything otherwise

salary_filter: int with the values:

1: Searches for jobs with salary $40k+
2: Searches for jobs with salary $60k+
3: Searches for jobs with salary $80k+
4: Searches for jobs with salary $100k+
5: Searches for jobs with salary $120k+
6: Searches for jobs with salary $140k+
7: Searches for jobs with salary $160k+
8: Searches for jobs with salary $180k+
9: Searches for jobs with salary $200k+
Defaults to searching for everything otherwise

"""


def scrape_linkedin_jobs(search_query, pages=1, date_filter=0, experience_filter=None, salary_filter=0, duplicate_job_threshold=3, max_jobs=-1):
    driver = webdriver.Chrome()  # Adjust the WebDriver path

    driver.get("https://www.linkedin.com/jobs")
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Cookies collected!")
    except FileNotFoundError:
        print("Cookies not found")
    driver.refresh()
    try:
        email_box = driver.find_element(By.XPATH, '//input[contains(@id, "session_key")]')
        email_box.send_keys(email_login)
        password_box = driver.find_element(By.XPATH, '//input[contains(@id, "session_password")]')
        password_box.send_keys(linkedin_password)
        submit_button = driver.find_element(By.XPATH, '//button[contains(@data-id, "sign-in-form__submit-btn")]')
        submit_button.click()
        time.sleep(2)
    except NoSuchElementException:
        pass
    try:
        email_pin = driver.find_element(By.XPATH, '//input[contains(@id, "input__email_verification_pin")]')
        time.sleep(10)
        creds = get_gmail_credentials()
        # Use the access token as the password
        auth_string = 'user=%s\1auth=Bearer %s\1\1' % (email_login, creds.token)

        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.authenticate('XOAUTH2', lambda x: auth_string)
        mail.select('inbox')

        # Search for emails
        result, data = mail.search(None, 'ALL')

        # Fetch Emails
        email_ids = data[0].split()
        email_ids.reverse()
        count = 0
        verification = None
        for e_id in email_ids:
            if count > 20:
                break
            result, email_data = mail.fetch(e_id, '(RFC822)')
            raw_email = email_data[0][1]
            # process the email
            # Example: Parsing the email content
            message = email.message_from_bytes(raw_email)
            if message["From"] == "LinkedIn <security-noreply@linkedin.com>" and "Here's your verification code" in message[
                "Subject"]:
                verification_string = "Here's your verification code "
                verification = message["Subject"][len(verification_string):].strip()
                break
            count += 1
            if verification == None:
                return
        email_pin.send_keys(verification)
        pin_submit = driver.find_element(By.XPATH, '//button[contains(@id, "email-pin-submit-button")]')
        pin_submit.click()
    except NoSuchElementException:
        pass
    try:
        search_box = driver.find_element(By.XPATH, '//input[contains(@class, "jobs-search-box__text-input")]')
    except NoSuchElementException:
        print("Something's up here. Maybe a captcha?")
        input("If there's a captcha, solve it and then press enter in the python console.")
        search_box = driver.find_element(By.XPATH, '//input[contains(@class, "jobs-search-box__text-input")]')
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(3)  # Wait for results to load

    job_postings = []
    job_counts = {}

    if date_filter in [1, 2, 3]:
        date_filter_button = driver.find_element(By.XPATH, '//button[contains(@id, "searchFilter_timePostedRange")]')
        date_filter_button.click()
        time.sleep(1)
        if date_filter == 1:
            past_month = driver.find_element(By.XPATH, '//label[contains(@for, "timePostedRange-r2592000")]')
            past_month.click()
        elif date_filter == 2:
            past_week = driver.find_element(By.XPATH, '//label[contains(@for, "timePostedRange-r604800")]')
            past_week.click()
        elif date_filter == 3:
            past_day = driver.find_element(By.XPATH, '//label[contains(@for, "timePostedRange-r86400")]')
            past_day.click()
        time.sleep(0.5)
        date_filter_button.click()
        time.sleep(4)

    if experience_filter is not None:
        experience_filter_button = driver.find_element(By.XPATH, '//button[contains(@id, "searchFilter_experience")]')
        experience_filter_button.click()
        for key in experience_filter:
            try:
                time.sleep(0.5)
                filter = driver.find_element(By.XPATH, f'//label[contains(@for, "experience-{key}")]')
                filter.click()
            except NoSuchElementException:
                print(f"Picked invalid experience level: {key}")
                continue
        experience_filter_button.click()
        time.sleep(4)

    if salary_filter in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        salary_filter_button = driver.find_element(By.XPATH, '//button[contains(@id, "searchFilter_salaryBucketV2")]')
        salary_filter_button.click()
        time.sleep(0.5)
        try:
            filter = driver.find_element(By.XPATH, f'//label[contains(@for, "salaryBucketV2-{salary_filter}")]')
            filter.click()
        except NoSuchElementException:
            print(f"Invalid salary value: {salary_filter}")
        salary_filter_button.click()
        time.sleep(4)

    # Loop through all job filters
    max_jobs_found = False
    for page in range(1, pages + 1):
        jobs = driver.find_elements(By.XPATH, '//div[contains(@class, "job-card-container--clickable")]')

        for i in range(0, 50):
            try:
                job = jobs[i]
            except IndexError:
                break
            driver.execute_script("return arguments[0].scrollIntoView(true);", job)
            jobs = driver.find_elements(By.XPATH, '//div[contains(@class, "job-card-container--clickable")]')
            job.click()
            time.sleep(0.75)
            try:
                job_card = driver.find_element(By.XPATH, '//div[contains(@class, "job-details-jobs-unified-top-card__content--two-pane")]')
            except NoSuchElementException:
                continue
            try:
                description = job_card.find_element(By.XPATH, '//div[contains(@id, "job-details")]').text
                description_full = job_card.find_element(By.XPATH, '//div[contains(@id, "job-details")]').get_attribute("innerHTML")
            except NoSuchElementException:
                description = "N/A"
                description_full = "N/A"
            try:
                title = job_card.find_element(By.XPATH, './/span[contains(@class, "job-details-jobs-unified-top-card__job-title-link")]').text
            except NoSuchElementException:
                title = "N/A"
            try:
                company = job_card.find_element(By.XPATH, './/a[contains(@class, "app-aware-link ")]').text
            except NoSuchElementException:
                company = "N/A"
            try:
                details = job_card.find_element(By.XPATH, './/div[contains(@class, "job-details-jobs-unified-top-card__primary-description-without-tagline mb2")]').text
            except NoSuchElementException:
                details = "N/A"
            job_dict = {
                'title': title,
                'company': company,
                'description': description,
                'description_html': description_full,
                'details' : details,
                'url' : driver.current_url
            }
            if company in job_counts:
                job_counts[company] += 1
            else:
                job_counts[company] = 1
            if job_counts[company] > duplicate_job_threshold:
                continue
            job_postings.append(job_dict)
            if max_jobs != -1 and len(job_postings) > max_jobs:
                max_jobs_found = True
                break
            print(job_dict)

        # Find and click the next page button
        if max_jobs_found:
            break
        try:
            next_page = driver.find_element(By.XPATH, f'//button[@aria-label="Page {page + 1}"]')
            next_page.click()
            time.sleep(2)  # Wait for the next page to load
            print(f"Page {page + 1}")
        except Exception as e:
            print("Reached the end of pages or encountered an error:", e)
            break
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    driver.quit()
    return job_postings

if __name__ == "__main__":
    scrape_linkedin_jobs("Software Engineer", 5, date_filter=1, experience_filter=[1, 2, 3], salary_filter=3)

