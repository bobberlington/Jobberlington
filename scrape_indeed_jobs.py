from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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



async def scrape_indeed_jobs(search_query, pages=1,
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
    tab = await driver.get("https://www.indeed.com/")
    try:
        await driver.cookies.load("cookies_indeed.dat")
        await tab.reload()
        print("Cookies collected!")
    except FileNotFoundError:
        print("Cookies not found")
    try:
        time.sleep(3)
        sign_in = await tab.find("Sign In", timeout=5)
        await sign_in.click()
        messagebox.showwarning(title="Not Logged In!",
                               message="Please log in first, then click OK after returning to the default indeed.com page. Your cookies will be saved after logging in.")
        await driver.cookies.save("cookies_indeed.dat")
    except Exception:
        pass

    job_title_search = await tab.select("input[id=text-input-what]")
    await job_title_search.send_keys(search_query)
    time.sleep(3)
    if location != "":
        job_location_search = await tab.select("input[id=text-input-where]")
        await job_location_search.send_keys(location)
        time.sleep(3)
    search_button = await tab.find("button[type=submit]")
    await search_button.click()
    job_postings = []
    job_counts = {}
    time.sleep(3)
    if date_filter in [0, 1, 2, 3]:
        date_filter_button = await tab.select("button[id*=fromAge_filter_button]")
        await date_filter_button.update()
        await date_filter_button.click()
        date_filter_dropdown = date_filter_button.parent
        date_filter_choice = await date_filter_dropdown.query_selector(f"a[data-testid=selection-pill-option-{date_filter}")
        await date_filter_choice.click()
        await tab
        time.sleep(2)
    if remote_filter in [0, 1, 2]:
        remote_filter_button = await tab.select("button[id*=remote_filter_button]")
        await remote_filter_button.update()
        await remote_filter_button.click()
        remote_filter_dropdown = remote_filter_button.parent
        remote_filter_choice = await remote_filter_dropdown.query_selector(f"a[data-testid=selection-pill-option-{remote_filter}")
        await remote_filter_choice.click()
        await tab
        time.sleep(2)
    # Values range 0-19
    if developer_skill_filter is not None:
        developer_skill_filter_button = await tab.select("button[id*=filter-taxo1]")
        await developer_skill_filter_button.update()
        await developer_skill_filter_button.click()
        for choice in developer_skill_filter:
            try:
                developer_skill_choice = await tab.find(choice, timeout=3)
                await developer_skill_choice.click()
                time.sleep(0.2)
            except TimeoutError:
                pass
        developer_submit = await tab.select("button[form=filter-taxo1-menu]")
        await developer_submit.click()
        await tab
        time.sleep(2)
    # Values range 0-4
    if job_type_filter is not None:
        job_type_filter_button = await tab.select("button[id*=filter-jobtype1]")
        await job_type_filter_button.update()
        await job_type_filter_button.click()
        for choice in job_type_filter:
            job_type_choice = await tab.find(choice, timeout=3)
            await job_type_choice.click()
            time.sleep(0.2)
        job_type_submit = await tab.select("button[form=filter-jobtype1-menu]")
        await job_type_submit.click()
        await tab
        time.sleep(2)
    if experience_filter in [0, 1, 2]:
        experience_filter_button = await tab.select("button[id*=expLvl_filter_button]")
        await experience_filter_button.update()
        await experience_filter_button.click()
        experience_filter_dropdown = experience_filter_button.parent
        experience_filter_choice = await experience_filter_dropdown.query_selector(f"a[data-testid=selection-pill-option-{experience_filter}")
        await experience_filter_choice.click()
        await tab
        time.sleep(2)
    if salary_filter in [0, 1, 2, 3, 4, 5, 6]:
        salary_filter_button = await tab.select("button[id*=salaryType_filter_button]")
        await salary_filter_button.update()
        await salary_filter_button.click()
        salary_filter_dropdown = salary_filter_button.parent
        salary_filter_choice = await salary_filter_dropdown.query_selector(f"a[data-testid=selection-pill-option-{salary_filter}")
        await salary_filter_choice.click()
        await tab
        time.sleep(2)
    if education_filter in [0, 1, 2, 3, 4]:
        education_filter_button = await tab.select("button[id*=education_filter_button]")
        await education_filter_button.update()
        await education_filter_button.click()
        education_filter_dropdown = education_filter_button.parent
        education_filter_choice = await education_filter_dropdown.query_selector(f"a[data-testid=selection-pill-option-{education_filter}")
        await education_filter_choice.click()
        await tab
        time.sleep(2)
    # Values range 0-4
    if developer_type_filter is not None:
        developer_type_button = await tab.select("button[id*=filter-taxo3]")
        await developer_type_button.click()
        for choice in developer_type_filter:
            developer_type_choice = await tab.find(choice, timeout=3)
            await developer_type_choice.click()
            time.sleep(0.2)
        developer_type_submit = await tab.select("button[form=filter-taxo3-menu]")
        await developer_type_submit.click()
        await tab
        time.sleep(2)
    # Values range 0-4
    if compensation_filter is not None:
        compensation_filter_button = await tab.select("button[id*=filter-taxo4]")
        await compensation_filter_button.click()
        for choice in compensation_filter:
            compensation_choice = await tab.find(choice, timeout=3)
            await compensation_choice.click()
            time.sleep(0.2)
        compensation_submit = await tab.select("button[form=filter-taxo4-menu]")
        await compensation_submit.click()
        await tab
        time.sleep(2)
    if distance_filter is not None:
        distance_filter_button = await tab.select("button[id*=filter-radius]")
        await distance_filter_button.update()
        await distance_filter_button.click()
        distance_filter_dropdown = distance_filter_button.parent
        distance_filter_choice = await distance_filter_dropdown.query_selector(f"a[data-testid=selection-pill-option-{education_filter}")
        await education_filter_choice.click()
        await tab
        time.sleep(2)




    for page in range(pages):
        await tab
        job_cards = await tab.select_all("a[class*=jcs-JobTitle]")
        for job_card in job_cards:
            try:
                await job_card.click()
                job = await tab.select("div[class*=fastviewjob]")
                await job.update()
                print("______________________Card Attributes__________________________")
                print(job_card.attributes)
                title = (await tab.select("h2[class*=jobsearch-JobInfoHeader-title]")).text
                print("_________________________________________")
                print(title)
                try:
                    company = (await job.query_selector("div[data-testid*=inlineHeader-companyName]")).text
                except AttributeError:
                    company = None
                try:
                    details = (await job.query_selector("div[data-testid*=inlineHeader-companyLocation]")).text
                except AttributeError:
                    details = None
                try:
                    description = (await job.query_selector("div[id*=jobDescriptionText]")).text
                    description_full = await (await job.query_selector("div[id*=jobDescriptionText]")).get_html()
                except AttributeError:
                    description = None
                    description_full = None

                datajk = ""

                for i in range(0, len(job_card.attributes)):
                    if job_card.attributes[i] == "data-jk":
                        datajk = job_card.attributes[i + 1]
                        break
                url = f"https://www.indeed.com/viewjob?jk={datajk}"
                job_dict = {
                    'title': title,
                    'company': company,
                    'description': description,
                    'description_html': description_full,
                    'details': details,
                    'url': url,
                    'logo': None
                }
                print(job_dict)
                job_postings.append(job_dict)
            except asyncio.exceptions.TimeoutError as e:
                print(e)
                input("")
            time.sleep(2)
        try:
            pagination = await tab.select("nav[aria-label*=pagination]")
            next_page = await pagination.query_selector("a[data-testid*=pagination-page-next]")
            if next_page is not None:
                await next_page.click()
            else:
                break
        except asyncio.exceptions.TimeoutError as e:
            print("This could be the last page")
            break


    return job_postings


if __name__ == "__main__":
    asyncio.run(scrape_indeed_jobs("Software Engineer", 5, date_filter=3, developer_skill_filter=["Python", "Java", "ASfsdfdf", "TypeScript"], developer_type_filter=[0], compensation_filter=[0], salary_filter=-1, max_jobs=4))

