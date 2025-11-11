---------------------Europages Wine Producer Scraper-----------------------------------

This project is a modular web scraping pipeline built for the Digiole internship challenge.
The goal is to build a "scalable lead generation" tool that gathers contact info (especially emails) for wine producers listed on Europages.

The final output is two CSV files:
-data/raw/links_wine.csv: A complete list of all company profile URLs.
-data/processed/emails_wine.csv: A clean list of company names, countries, and their emails.


---------------------------------Approach----------------------------------------------


This pipeline is broken into three small, focused modules that pass data to each other.

Module 1 (01_link_collector.py): Its only job is to visit the Europages search results and collect every single company profile URL.

Module 2 (02_email_extractor.py): It reads the URLs from Module 1, visits each company's profile, finds their actual website, and then hunts for an email address.

Module 3 (03_data_cleaner.py): It takes the messy data from Module 2, throws out junk emails (like info@wordpress.com or image@4x.png), and produces the final, clean CSV.


-------------------------------Challenges faced----------------------------------------

Pop-ups: The scraper only failed because I ran it headless; once I watched it in a real browser I spotted the cookie banner and location “Keep” dialog and added first-page handlers.

Pagination: Inspecting the actual Next button showed the real /search/page/N?q=… pattern, so the script now generates those URLs and stops when the button turns disabled or at a specified number of pages (mainly for quick tests).

Staled Page: The correct pagination worked, but the log showed 0 new links on every page. Selenium was scraping the old page's data. I fixed this by adding a wait (EC.staleness_of) to ensure the previous page's content was gone before scraping the new one.

Finding right selectors: Common selectors didn't work so I had to inspect the html of the page in devtools to find the right and stable ones.

Email Hunting: after a homepage miss it looks for multilingual contact links (for example “contact”, “contatti”, “kontakt”) using an XPath with . so nested text is matched.

----------------------------------Future Improvements----------------------------------

LLM use:
-Giving the LLM a whole contact page and asking it to pull out specific roles instead of just the first email it sees.
-Having an LLM read the "About Us" page and automatically classify the company (e.g., "Producer" "Distributor") to score the lead's quality.

Make it More Robust and Efficient: The selectors (like a.company-name) are hard-coded for this specific Europages website. If another sector uses a slightly different template, the whole thing breaks. It also starts two separate Selenium sessions, which is slow. A future version could store selectors in the config file for different sectors and it could run parallel worker threads to reduce elaboration times drastically.
