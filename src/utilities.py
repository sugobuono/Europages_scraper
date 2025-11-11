import csv
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def make_dir(path):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)



def build_webdriver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    return webdriver.Chrome(options=options)


















# --- IGNORE ---
# def save_records_to_csv(records, path):
#     make_dir(path)
#     records = list(records)
#     if not records:
#         with open(path, "w", newline="", encoding="utf-8") as handle:
#             handle.write("")
#         return
#     keys = list(records[0].keys())
#     with open(path, "w", newline="", encoding="utf-8") as handle:
#         writer = csv.DictWriter(handle, fieldnames=keys)
#         writer.writeheader()
#         for item in records:
#             writer.writerow(item)
#