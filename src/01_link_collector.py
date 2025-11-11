import csv
import os
import sys
import time
from pathlib import Path

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from urllib.parse import urljoin

from config import DEFAULT_CONFIG
from utilities import build_webdriver, make_dir


PAGINATION_NEXT_SELECTOR = "a[data-test='pagination-next']"
PROFILE_LINK_SELECTORS = [
    "a[data-test='company-name']",
]

def get_page_url(config, page_num):
    base_url = config.base_search_url.rstrip("/")
    if "?" in base_url:
        base_search, query = base_url.split("?", 1)
    else:
        base_search, query = base_url, ""

    if page_num == 1:
        return base_url
    path = f"{base_search}/page/{page_num}"
    if query:
        return f"{path}?{query}"
    return path


def collect_profile_links(config):
    links = []
    seen = set()
    driver = build_webdriver(headless=config.headless)
    wait = WebDriverWait(driver, 20)
    reference_element = None

    try:
        max_pages = min(config.max_pages, 6)
        for page_num in range(1, max_pages + 1):
            page_url = get_page_url(config, page_num)
            print(f"\n--- Loading Page {page_num}: {page_url} ---")
            driver.get(page_url)

            if page_num == 1:
                print("Handling pop-ups...")
                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[normalize-space()='Keep']")
                        )
                    ).click()
                    print("Clicked 'Keep'.")
                    time.sleep(1)
                except Exception:
                    print("Location pop-up not found.")

                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[normalize-space()='Accept all cookies']")
                        )
                    ).click()
                    print("Clicked 'Accept all cookies'.")
                    time.sleep(1)
                except Exception:
                    print("Cookie banner not found.")

            if reference_element is not None:
                print("Waiting for old page content to go stale...")
                try:
                    wait.until(EC.staleness_of(reference_element))
                    print("Old content is stale. Page has refreshed.")
                except TimeoutException:
                    print("Timed out waiting for staleness. Page may not have loaded.")
                    break

            try:
                cards = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, PROFILE_LINK_SELECTORS[0])
                    )
                )
                print(f"Found {len(cards)} elements matching selector.")
                if cards:
                    reference_element = cards[0]
                time.sleep(1)
            except TimeoutException:
                print(f"Timed out waiting for links on page {page_num}. Stopping.")
                break

            new_links = 0
            rejected = []
            for card in cards:
                href = card.get_attribute("href")
                if not href:
                    continue
                absolute_href = urljoin(config.base_search_url, href)
                if absolute_href in seen:
                    continue
                if "europages.co.uk" not in absolute_href:
                    rejected.append(absolute_href)
                    continue
                if "javascript:void" in absolute_href:
                    rejected.append(absolute_href)
                    continue
                seen.add(absolute_href)
                links.append(absolute_href)
                new_links += 1

            print(f"Found {len(cards)} links on this page; {new_links} new. Total unique: {len(links)}")

            if rejected:
                print(f"  Ignored {len(rejected)} junk links. Examples:")
                for junk in list(dict.fromkeys(rejected))[:5]:
                    print(f"    - {junk}")

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, PAGINATION_NEXT_SELECTOR)
                next_class = next_button.get_attribute("class") or ""
                if "disabled" in next_class.lower():
                    print("'Next page' button is disabled. Reached the end.")
                    break
            except NoSuchElementException:
                print("No 'next page' button found. Reached the end.")
                break

            time.sleep(1.5)
    finally:
        driver.quit()

    return links


def write_links_csv(links, output_path):
    make_dir(str(output_path))
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["profile_url"])
        for link in links:
            writer.writerow([link])


def main(output_path=None):
    config = DEFAULT_CONFIG
    if output_path is None:
        destination = Path(os.path.join(config.output_dir, "raw", "links_wine.csv"))
    else:
        destination = output_path
    links = collect_profile_links(config)
    if not links:
        raise SystemExit("No profile links discovered; adjust selectors or configuration.")
    write_links_csv(links, destination)
    print(f"Saved {len(links)} profile URLs to {destination}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(output_path=Path(sys.argv[1]))
    else:
        main()