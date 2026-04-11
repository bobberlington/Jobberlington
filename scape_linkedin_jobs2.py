import time
from credentials import email_login, linkedin_password
import imaplib
import email
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pickle
from tkinter import messagebox
import zendriver as uc
from asyncio.exceptions import TimeoutError
import asyncio



async def scrape_linkedin_jobs(search_query, pages=1,
                             date_filter=-1,
                             remote_filter=-1,
                             developer_skill_filter = None,
                             job_type_filter = None,
                             experience_filter=None,
                             salary_filter=-1,
                             education_filter=-1,
                             developer_type_filter = None,
                             compensation_filter = None,
                             distance_filter = None,
                             duplicate_job_threshold=3,
                             max_jobs=0,
                             browser="",
                             location=""):
    driver = await uc.start()
    tab = await driver.get("https://www.linkedin.com/jobs")
    try:
        await driver.cookies.load("cookies_linkedin.dat")
        await tab.reload()
        print("Cookies collected!")
    except FileNotFoundError:
        print("Cookies not found")
    try:
        time.sleep(3)
        sign_in = await tab.find("Sign In", timeout=5)
        await sign_in.click()
        messagebox.showwarning(title="Not Logged In!",
                               message="Please log in first, then click OK after returning to the default linkedin.com page. Your cookies will be saved after logging in.")
        await driver.cookies.save("cookies_linkedin.dat")
    except Exception:
        pass

    job_title_search = await tab.select("input[placeholder=Title, skill or Company]")
    await job_title_search.send_keys(search_query)
    time.sleep(3)
    if location != "":
        job_location_search = await tab.select("input[placeholder=City, state, or zip code]")
        await job_location_search.send_keys(location)
        time.sleep(3)
    await job_title_search.send_keys("\n")
    job_postings = []
    job_counts = {}
    time.sleep(3)
    # Scrolling down the job screen
    if date_filter in [1, 2, 3]:
        date_filter_button = await tab.find("Date posted", timeout=5)
        await date_filter_button.update()
        await date_filter_button.click()
        await tab
        time.sleep(2)
    if experience_filter is not None:
        experience_filter_button = await tab.find("Experience level", timeout=5)
        await experience_filter_button.update()
        await experience_filter_button.click()
        await tab
        time.sleep(2)

    if salary_filter in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        salary_filter_button = await tab.find("Salary", timeout=5)
        await salary_filter_button.update()
        await salary_filter_button.click()
        await tab
        time.sleep(2)
    # Values range 0-4
    if remote_filter is not None:
        remote_filter_button = await tab.find("Remote", timeout=5)
        await remote_filter_button.update()
        await remote_filter_button.click()
        await tab
        time.sleep(2)


    for page in range(pages):
        await tab
        job_cards = await tab.select_all("div[class*=job-card-container--clickable]")
        for job_card in job_cards:
            try:
                await job_card.click()
                job = await tab.select("div[class*=jobs-search__job-details--wrapper]")
                await job.update()
                print("______________________Card Attributes__________________________")
                print(job.attributes)
                title = (await job.select("h1[class*=t-24 t-bold inline]")).text
                print("_________________________________________")
                print(title)
                try:
                    company = (await job.query_selector("div[job-details-jobs-unified-top-card__company-name]")).text
                except AttributeError:
                    company = None
                try:
                    details = (await job.query_selector("div[ob-details-jobs-unified-top-card__tertiary-description-container")).text
                except AttributeError:
                    details = None
                try:
                    description = (await job.query_selector("div[id*=job-details]")).text
                    description_full = await (await job.query_selector("div[id*=job-details]")).get_html()
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
                input("")
            time.sleep(2)
        try:
            next_page = await tab.select("button[class*=jobs-search-pagination__button--next]")
            if next_page is not None:
                await next_page.click()
            else:
                break
        except asyncio.exceptions.TimeoutError as e:
            print("This could be the last page")
            break


    return job_postings


if __name__ == "__main__":
    asyncio.run(scrape_linkedin_jobs("Software Engineer", 5, date_filter=3, developer_skill_filter=["Python", "Java", "ASfsdfdf", "TypeScript"], developer_type_filter=[0], compensation_filter=[0], salary_filter=-1, max_jobs=4))

