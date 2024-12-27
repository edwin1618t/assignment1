import uuid
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient

 
PROXYMESH_URL = "http://edwin_8838:.AQ6.NUEvrYmkeL@fr.proxymesh.com:31280"   
 
client = MongoClient('mongodb://localhost:27017/')
db = client['stirx']  
collection = db['trending_topics']

 
options = Options()
options.add_argument(f'--proxy-server={PROXYMESH_URL}')

 
geckodriver_path = 'C:/Users/ed200/Documents/webdriver/geckodriver-v0.35.0-win64/geckodriver.exe'  
service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

def login(driver, username, email, password):
    try:
        # Open x Login Page
        driver.get('https://x.com/i/flow/login?lang=en')
        print("Navigated to the  x login page.")

        # Wait for Username Field and Enter Username
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]'))
        )
        print("Username field found. Entering username...")
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)

        # Handle Unusual Activity (Enter Email)
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]'))
            )
            print("Unusual activity detected. Entering email...")
            email_field.send_keys(email)
            email_field.send_keys(Keys.RETURN)
        except Exception:
            print("No unusual activity prompt detected. Proceeding with login...")

        # Wait for Password Field and Enter Password
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password"]'))
        )
        print("Password field found. Entering password...")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Wait for a Key Element on the Homepage to Confirm Successful Login
        WebDriverWait(driver, 30).until(
            EC.visibility_of_all_elements_located((By.XPATH, '//div[@aria-label="Timeline: Trending now"]//a'))
        )
       
        print("Login successful!")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def scrape_twitter_trends():
    try:
        # Ensure the "Trending now" section is loaded
        print("Waiting for trending topics section to load...")
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Timeline: Trending now"]'))
        )

        # Scrape Trending Topics from "What's Happening"
        trend_elements = driver.find_elements(By.XPATH, '//div[@aria-label="Timeline: Trending now"]//div[@data-testid="trend"]')
        print(f"Found {len(trend_elements)} trend elements.")

        # Extracting trends and post counts
        trend_names = []
        for trend in trend_elements[:5]:  # Limit to top 5 trends
            try:
                category = trend.text  # Directly using the trend text
                trend_names.append(category)
            except Exception as e:
                print(f"Error extracting trend data: {e}")
                continue  # Skip  

        # Debugging: Print extracted trend names
        print(f"Trend Names: {trend_names}")

        # If fewer than 5 trends, fill the remaining with "N/A"
        while len(trend_names) < 5:
            trend_names.append("N/A")

        # Get IP Address
        ip_address = requests.get("http://ipinfo.io/ip", proxies={"http": PROXYMESH_URL}).text.strip()
        print(f"Using IP address: {ip_address}")

        # Create Data  
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now()
        data = {
            "_id": unique_id,
            "trend1": trend_names[0],
            "trend2": trend_names[1],
            "trend3": trend_names[2],
            "trend4": trend_names[3],
        
            "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "ip_address": ip_address
        }

        # Insert data into MongoDB
        collection.insert_one(data)
        print("Data successfully inserted into MongoDB.")
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()

# Run Scraper
if __name__ == "__main__":
     
    twitter_username = 'EXxdex53894'  
    twitter_email = 'edxbcmxxdex@gmail.com'   
    twitter_password = '20203500152020'   

    # Login 
    if login(driver, twitter_username, twitter_email, twitter_password):
        # After login, scrape trending topics
        result = scrape_twitter_trends()
        if result:  
            print("\nTrending Topics Scraped and Inserted into MongoDB:")
            print(result)
  