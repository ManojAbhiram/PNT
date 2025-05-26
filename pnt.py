from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Comment this out if you want to see the browser
driver = webdriver.Chrome(options=options)

driver.get("https://rera.odisha.gov.in/projects/project-list")
wait = WebDriverWait(driver, 10)

# Wait for the View Details buttons to load
wait.until(EC.presence_of_element_located((By.LINK_TEXT, "View Details")))

# Get first 6 project "View Details" links
view_buttons = driver.find_elements(By.LINK_TEXT, "View Details")[:6]

project_data = []

for index, button in enumerate(view_buttons):
    try:
        project_url = button.get_attribute("href")
        driver.execute_script("window.open(arguments[0]);", project_url)
        driver.switch_to.window(driver.window_handles[1])

        wait.until(EC.presence_of_element_located((By.ID, "pills-project-tab")))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Project Overview
        overview_div = soup.find("div", id="pills-project")
        rera_no = overview_div.find(string="RERA Regd. No.").find_next().text.strip()
        project_name = overview_div.find(string="Project Name").find_next().text.strip()

        # Switch to Promoter Details tab
        driver.find_element(By.ID, "pills-promoter-tab").click()
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        promoter_div = soup.find("div", id="pills-promoter")

        company_name = promoter_div.find(string="Company Name").find_next().text.strip()
        office_address = promoter_div.find(string="Registered Office Address").find_next().text.strip()
        gst_no = promoter_div.find(string="GST No.").find_next().text.strip()

        project_data.append({
            "RERA Regd. No.": rera_no,
            "Project Name": project_name,
            "Company Name": company_name,
            "Registered Office Address": office_address,
            "GST No.": gst_no
        })

        print(f"[{index+1}] Scraped: {project_name}")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"[{index+1}] Error: {e}")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

driver.quit()

# Save to CSV
df = pd.DataFrame(project_data)
df.to_csv("rera_projects_odisha.csv", index=False)
print("\n Data saved to 'rera_projects_odisha.csv'")
