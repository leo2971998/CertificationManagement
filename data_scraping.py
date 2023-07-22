# data_scraping.py
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_certification_level(name):
    if "Fundamentals" in name:
        return 1
    elif "Associate" in name:
        return 2
    elif "Expert" in name:
        return 3
    elif "Specialty" in name:
        return "Specialty"
    else:
        return None

def get_certification_info(certification_html):
    name = certification_html.text.strip()
    level = get_certification_level(name)

    parent_element = certification_html.find_element(By.XPATH, "..")  # Get the parent element
    code = parent_element.find_element(By.CLASS_NAME, "is-comma-delimited").text.strip()  # Get the code

    image_element = parent_element.find_element(By.CLASS_NAME, "card-template-icon")
    image_url = image_element.get_attribute("src")

    return code, name, level, False, image_url

def scrape_and_store():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://learn.microsoft.com/en-ca/certifications/browse/?resource_type=certification&products=azure"
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    certifications_html = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card-title")))

    certifications = [get_certification_info(cert) for cert in certifications_html]

    driver.quit()

    conn = sqlite3.connect('certifications.db')
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT, 
            name TEXT, 
            level TEXT, 
            owned BOOLEAN, 
            image_url TEXT
        )
    """)

    c.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_certifications_code 
        ON certifications (code)
    """)

    for certification in certifications:
        try:
            c.execute("""
                INSERT INTO certifications (code, name, level, owned, image_url) 
                VALUES (?, ?, ?, ?, ?)
            """, certification)
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
