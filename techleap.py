import time
import json
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()


# a function to send emails
def send_email(acc_count, alumni_count, diff_table):
    # SIB configuration
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = os.getenv("SIB_API_KEY")
    # create an instance of the API class
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    # create email vars
    subject = f"Scraper News: {acc_count} Accelerators, {alumni_count} Alumni"
    diff_table = diff_table[["accelerator", "alumni_name", "alumni_year"]]
    diff_table.columns = ["Accelerator", "Company", "Founded On"]
    html_table = diff_table.to_html(index=False)
    style_content = "<style>table {border-collapse: collapse; width: 100%; font-size: 14px; margin-bottom: 20px;} table th, table td {padding: 10px; text-align: left; vertical-align: top; border: 1px solid #ccc;} table th { background-color: #f5f5f5;font-weight: bold;} table tr:nth-child(even) td {background-color: #f9f9f9;}</style>"
    html_content = f"<html><head>{style_content}</head><body><h1>Scraper Update</h1><p>New Accelerators: {acc_count}</p><p>New Alumnis: {alumni_count}</p>{html_table}</body></html>"
    sender = {"name": "Scraper #001", "email": os.getenv("SIB_SENDER")}
    to = [{"email": os.getenv("SIB_RECIPIENT"), "name": "Scraper User"}]
    headers = {"EMAIL_SNATHJR": "snathjr-1234"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        reply_to=sender,
        headers=headers,
        html_content=html_content,
        sender=sender,
        subject=subject,
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
    else:
        print("Sent an email successfully.")


# previous alumnis
prev_alumnis = {
    "accelerator": [],
    "accelerator_link": [],
    "alumni_name": [],
    "alumni_link": [],
    "alumni_year": [],
}

# read previous data
if os.path.exists("techleap.json"):
    with open("techleap.json", "r") as f:
        prev_alumnis = json.load(f)

prev_alumnis = pd.DataFrame(prev_alumnis)
# -------


# a function to intercept the modal
def intercept_modal(driver):
    try:
        modal = driver.find_element(By.CLASS_NAME, "ReactModal__Overlay")
        # send javascript to delete modal
        driver.execute_script("arguments[0].remove();", modal)
    except:
        pass
    else:
        print("X> Modal found and deleted")


# a function to intercept the modal
def techleap_login(driver, username, password):
    login_btn = driver.find_element(By.CLASS_NAME, "login-button")
    login_btn.click()
    # Wait for the page to load
    time.sleep(5)
    # find the username field
    username_field = driver.find_element(By.ID, "username")
    # find the password field
    password_field = driver.find_element(By.ID, "password")
    # input username and password
    username_field.send_keys(username)
    password_field.send_keys(password)
    # find the login button
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    # click the login button
    submit_button.click()
    # Wait for the page to load
    time.sleep(5)


def sort_by_column(driver, column):
    # check if the table exists
    alumni_table = None
    try:
        intercept_modal(driver)
        alumni_table = driver.find_element(By.CLASS_NAME, "table")
    except:
        print("No alumni table found, nothing to be done")
    if alumni_table:
        # try to find the table-column-header launchDate sortable has-dropdown
        intercept_modal(driver)
        launchDate = driver.find_element(By.CLASS_NAME, column)
        sort_btn = launchDate.find_element(
            By.CLASS_NAME, "table-column-header__sort-button"
        )
        sort_btn.click()
        # Wait for the page to load
        time.sleep(5)


def fetch_alumnis(driver, accelerator):
    # accelerator's alumni list
    alumnis = []
    # get required data from the accelerator
    acc_name = accelerator["name"]
    acc_link = accelerator["internal_url"]
    # load the accelerator page
    driver.get(acc_link)
    # Wait for the page to load
    time.sleep(5)
    # check if any modal pops up and intercept it
    intercept_modal(driver)
    # try to find the alumni tab
    tab_link = driver.find_elements(By.CLASS_NAME, "tab-links")[0]
    # try to find the alumni button
    alumni_btn = tab_link.find_elements(By.TAG_NAME, "button")[1]
    # click the alumni button
    alumni_btn.click()
    # Wait for the page to load
    time.sleep(5)
    # sort by launch date
    sort_by_column(driver, "launchDate")
    # check if any modal pops up and intercept it
    intercept_modal(driver)
    # try to find table list items
    table_list_items = driver.find_elements(By.CLASS_NAME, "table-list-item")
    # loop over table list items to get the alumni
    for table_list_item in table_list_items:
        alumni_name = table_list_item.find_element(
            By.CLASS_NAME, "entity-name__name-text"
        )
        alumni_link = alumni_name.get_attribute("href")
        alumni_year = table_list_item.find_element(By.TAG_NAME, "time")
        # append data to alumnis list
        alumnis.append(
            {
                "accelerator": acc_name,
                "accelerator_link": acc_link,
                "alumni_name": alumni_name.text,
                "alumni_link": alumni_link,
                "alumni_year": alumni_year.text,
            }
        )
    return alumnis


# -------

# pass headless options
options = webdriver.ChromeOptions()
# run chrome in headless mode
options.headless = False

# let's create a chrome driver
driver = webdriver.Chrome(options=options)

# this is the url we want to visit
url = "https://finder.techleap.nl/investors.accelerators"

# let's now open the page we want to visit
driver.get(url)
# implicitly wait for a page to load
time.sleep(5)


# try to find the cookie button
try:
    cookie_accept_btn = driver.find_element(By.ID, "cw-yes")
    cookie_accept_btn.click()
except:
    print("!> Cookie button not found, should be alright.")
# Wait for the data to load
time.sleep(1)

# try to login
techleap_login(driver, os.getenv("TECHLEAP_USER"), os.getenv("TECHLEAP_PASS"))

# go back to the page of accelerators
driver.get(url)
# implicitly wait for a page to load
time.sleep(5)

# now lets try to find all the accelerators
accelerators = driver.find_elements(By.CLASS_NAME, "table-list-item")

# this can be treated as our database
database = {}

# lets loop over the accelerators
for accelerator in accelerators:
    acc_name = accelerator.find_element(By.CLASS_NAME, "entity-name__name-text")
    acc_internal_link = acc_name.get_attribute("href")
    database[acc_name.text] = {"name": acc_name.text, "internal_url": acc_internal_link}


# create an empty list to store alumnis
alumnis = []

# loop over the database to fetch more data
for accelerator in database.values():
    print("=> Fetching data for: ", accelerator["name"])
    acc_alumnis = fetch_alumnis(driver, accelerator)
    print(" < Found Alumnis: ", len(acc_alumnis))
    alumnis.extend(acc_alumnis)

# save the data to a json file
with open("techleap.json", "w") as f:
    json.dump(alumnis, f)

# analyse the current alumnis
current_alumnis = pd.DataFrame(alumnis)
# create difference between current and previous alumnis
merged = current_alumnis.merge(prev_alumnis, how="outer", indicator=True)
diff = merged[merged["_merge"] == "left_only"]
# calculate new accelerator count and new alumni count
num_new_accelerators = diff["accelerator"].unique().shape[0]
num_new_alumnis = diff["alumni_name"].unique().shape[0]
# send an email with the report
if num_new_accelerators > 0 or num_new_alumnis > 0:
    send_email(num_new_accelerators, num_new_alumnis, diff)
else:
    print("No new data found. Nothing to be done.")
