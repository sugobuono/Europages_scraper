import pandas as pd
import re
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utilities import build_webdriver


INPUT_FILE = "data/raw/links_wine.csv"
OUTPUT_FILE = "data/raw/raw_email_data.csv"
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
NAME_SELECTOR = "a.company-name"
COUNTRY_SELECTOR = "span.vis-flag + span"
WEBSITE_BTN_SELECTOR = "a.website-button"

def extract_email_data():
    try:
        links_df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Run 01_link_collector.py first.")
        return

    driver = build_webdriver(headless=True)
    wait = WebDriverWait(driver, 10)
    results = []
    max_profiles = 6 

    for index, row in links_df.head(max_profiles).iterrows():
        
        profile_url = row.get("profile_url", "")
        if not profile_url.startswith("http"):
            profile_url = "https://www.europages.co.uk" + profile_url

        print(f"\nProcessing {index + 1}/{min(len(links_df), max_profiles)}: {profile_url}")

        try:
            
            driver.get(profile_url)
            if index == 0:
                
                print("  -> Handling pop-ups...")
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Keep']"))).click()
                except Exception: pass
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Accept all cookies']"))).click()
                except Exception: pass
            
            
            company_name = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, NAME_SELECTOR))).text
            country = driver.find_element(By.CSS_SELECTOR, COUNTRY_SELECTOR).text
            website_button = driver.find_element(By.CSS_SELECTOR, WEBSITE_BTN_SELECTOR)
            external_url = website_button.get_attribute("href")

            if not external_url:
                print("  -> No external website link on profile.")
                continue

            
            print(f"  -> Visiting external site: {external_url}")
            driver.get(external_url)
            time.sleep(2)
            final_url = driver.current_url
            print(f"  -> Final URL: {final_url}")
            page_source = driver.page_source
            found_emails = list(dict.fromkeys(re.findall(EMAIL_REGEX, page_source)))

            
            if not found_emails:
                print("  -> No emails on homepage, searching for 'Contact' link...")
                try:
                    
                    contact_terms = ["contact", "contatti", "kontakt", "contacto", "contato", "contactez-nous"]
                    
                    normalized_text = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" 
                    xpath_conditions = " or ".join([f"contains({normalized_text}, '{term}')" for term in contact_terms])
                    contact_xpath = f"//a[{xpath_conditions}]"
                    contact_link = driver.find_element(By.XPATH, contact_xpath)
                    
                    contact_href = contact_link.get_attribute('href')
                    if contact_href:
                        print(f"  -> Found contact page, visiting: {contact_href}")
                        driver.get(contact_href)
                        time.sleep(2)
                        page_source = driver.page_source
                        found_emails = list(dict.fromkeys(re.findall(EMAIL_REGEX, page_source)))
                except NoSuchElementException:
                    print("  -> No 'Contact' link found.")
                except Exception as e:
                    print(f"  -> Error navigating to contact page: {e}")
            
            
            if found_emails:
                print(f"  -> SUCCESS: Found emails: {found_emails}")
                results.append({
                    "Name": company_name, "Country": country,
                    "Email": found_emails[0], 
                    "Source_Profile": profile_url, "Website": final_url
                })
            else:
                print("  -> No emails found on website or contact page.")

        except Exception as e:
            print(f"  -> UNKNOWN ERROR: {e}. Skipping.")

    driver.quit()

    if results:
        output_df = pd.DataFrame(results)
        output_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nExtraction complete. Saved {len(output_df)} results to {OUTPUT_FILE}")
    else:
        print("\nExtraction complete. No emails found.")

if __name__ == "__main__":
    extract_email_data()