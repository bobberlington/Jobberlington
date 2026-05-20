import time
from credentials import email_login, linkedin_password
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import messagebox
import zendriver as uc
from asyncio.exceptions import TimeoutError
import asyncio
import re

clean = re.compile(r'<.*?>')
spaces = re.compile(r'\s+')

def cleanhtml(raw_html):
  cleantext = re.sub(clean, '', raw_html)
  cleantext = re.sub(spaces, ' ', cleantext)
  return cleantext


async def scrape_linkedin_jobs(search_query, pages=1,
                             date_filter=None,
                             remote_filter=None,
                             experience_filter=None,
                             salary_filter=None,
                             location=""):
    driver = await uc.start()
    tab = await driver.get("https://www.linkedin.com/jobs")
    sleepytime = False
    try:
        await driver.cookies.load("cookies_linkedin.dat")
        await tab.reload()
        print("Cookies collected!")
    except FileNotFoundError:
        print("Cookies not found")
        sleepytime = True
    try:
        time.sleep(3)
        email_box = await tab.select("input[id='session_key']", timeout=5)
        await email_box.focus()
        await email_box.send_keys(email_login)
        time.sleep(2)
        password_box = await tab.select("input[id='session_password'", timeout=5)
        await password_box.focus()
        await password_box.send_keys(linkedin_password)
        time.sleep(1)
        submit = await tab.select("button[type='submit']", timeout=5)
        await submit.mouse_move()
        await submit.mouse_click()
        if sleepytime:
            time.sleep(30)
        print("Trying to save cookies.")
        await driver.cookies.save("cookies_linkedin.dat")
        print("Cookie saved!")
    except Exception:
        pass

    starting_url = "https://www.linkedin.com/jobs/search/"
    date_url = ""
    experience_url = ""
    location_url = f"&geoId={location}"
    salary_url = ""
    remote_url = ""
    query_url = f"&keywords={search_query.lower().replace(' ', '%20')}"

    job_postings = []
    job_counts = {}
    # Scrolling down the job screen
    if date_filter in ["Any time", "Past month", "Past week", "Past 24 hours"]:
        date_url_dict = {"Any time": "",
                         "Past month": "&f_TPR=r2592000",
                         "Past week": "&f_TPR=r604800",
                         "Past 24 hours": "&f_TPR=r86400"}
        date_url = date_url_dict[date_filter]

    if experience_filter is not None:
        experience_url_dict = {"Internship" : "1",
                               "Entry level" : "2",
                               "Associate" : "3",
                               "Mid-Senior level": "4",
                               "Director": "5",
                               "Executive": "6"
                               }
        # The url is structured f_E=1%2C2%2C3, where the first value is numbered, then all subsequent values are prefixed with %2C
        experience_url = "&f_E="
        for i in range(len(experience_filter)):
            if i > 0:
                experience_url += f"%2C{experience_url_dict[experience_filter[i]]}"
            else:
                experience_url += f"{experience_url_dict[experience_filter[i]]}"

    if salary_filter in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        salary_url = f"&f_SB2={salary_filter}"
    # Values range 0-4
    if remote_filter is not None:
        remote_url_dict = {"On-site": "1",
                               "Hybrid": "2",
                               "Remote": "3",
                               }
        # The url is structured f_E=1%2C2%2C3, where the first value is numbered, then all subsequent values are prefixed with %2C
        remote_url = "&f_WT="
        for i in range(len(remote_filter)):
            if i > 0:
                remote_url += f"%2C{remote_url_dict[remote_filter[i]]}"
            else:
                remote_url += f"{remote_url_dict[remote_filter[i]]}"

    url = f"{starting_url}?{experience_url}{salary_url}{date_url}{remote_url}{location_url}{query_url}"
    tab = await driver.get(url)
    current_page = 0
    all_job_ids = []
    job_count = 0
    max_jobs = int(pages * 25)


    while current_page < pages :
        if job_count > max_jobs:
            break
        await tab
        time.sleep(10)
        job_ids = []
        job_cards = await tab.select_all("li[data-occludable-job-id]")
        print(len(job_cards))
        current_id_length = len(all_job_ids)
        for card in job_cards:
            job_id = card.get("data-occludable-job-id")
            if job_id not in all_job_ids:
                all_job_ids.append(job_id)
                job_ids.append(job_id)
        print(job_ids)
        if len(all_job_ids) == 0:
            print("End of jobs?")
            break
        elif len(all_job_ids) == current_id_length:
            all_job_ids = []
            current_page += 1
            page_url = f"&start={current_page * 25}"
            url = f"{starting_url}?{experience_url}{salary_url}{date_url}{remote_url}{location_url}{query_url}{page_url}"
            tab = await driver.get(url)
            await tab
            continue

        for job_id in job_ids:
            if job_count > max_jobs:
                break
            try:
                job_card_location = await tab.select(f"li[data-occludable-job-id='{job_id}']", timeout = 2)
                await job_card_location.scroll_into_view()
                job_card = await tab.select(f"div[data-job-id='{job_id}']", timeout = 2)
                await job_card.click()
                await job_card.update()
                job = await tab.select("div[class='jobs-search__job-details--wrapper']")
                try:
                    title = (await job.query_selector("h1[class*='t-24 t-bold inline']")).text
                except AttributeError:
                    title = None
                try:
                    company = (await job.query_selector("div[class*='job-details-jobs-unified-top-card__company-name']")).text
                except AttributeError:
                    company = None
                try:
                    details = (await job.query_selector("div[ob-details-jobs-unified-top-card__tertiary-description-container")).text
                except AttributeError:
                    details = None
                try:
                    description_full = await (await job.query_selector("div[id*=job-details]")).get_html()
                    description = cleanhtml(cleanhtml(description_full).replace("\n", " "))
                except AttributeError:
                    description = None
                    description_full = None

                job_dict = {
                    'title': title,
                    'company': company,
                    'description': description,
                    'description_html': description_full,
                    'details': details,
                    'url': tab.url,
                    'logo': None
                }
                print(job_dict)
                job_postings.append(job_dict)
            except asyncio.exceptions.TimeoutError as e:
                print(e)
                continue
            job_count += 1
            time.sleep(1)


    return job_postings


if __name__ == "__main__":
    asyncio.run(scrape_linkedin_jobs("Software Engineer", 5, location="106233382", date_filter="Any time", experience_filter=["Internship", "Associate"], salary_filter=3, remote_filter=["On-site", "Hybrid", "Remote"]))

