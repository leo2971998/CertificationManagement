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



# URL of the webpage containing certification info
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = "https://learn.microsoft.com/en-ca/certifications/browse/?resource_type=certification&products=azure"
driver.get(url)

# Wait up to 10 seconds for the certifications to be loaded
wait = WebDriverWait(driver, 10)

certifications_html = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card-title")))

# Extract certification info into a list before closing the driver
certifications = [get_certification_info(cert) for cert in certifications_html]

driver.quit()

# Open SQLite connection
conn = sqlite3.connect('certifications.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute("CREATE TABLE IF NOT EXISTS certifications (code TEXT PRIMARY KEY, name TEXT, level TEXT, owned BOOLEAN, image_url TEXT)")

# Loop over each certification and insert into the SQLite database
for certification in certifications:
    c.execute("INSERT OR REPLACE INTO certifications (code, name, level, owned, image_url) VALUES (?, ?, ?, ?, ?)", certification)

# Commit changes and close connection
conn.commit()

# Fetch and print all data
c.execute("SELECT * FROM certifications")
rows = c.fetchall()
for row in rows:
    print(row)

conn.close()
