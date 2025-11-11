import pandas as pd
import re
import os
from pathlib import Path


RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
INPUT_FILE = os.path.join(RAW_DATA_DIR, "raw_email_data.csv")
OUTPUT_FILE = os.path.join(PROCESSED_DATA_DIR, "emails_wine.csv")


VALID_EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


JUNK_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
    "aol.com", "icloud.com", "example.com", "wix.com", 
    "wordpress.com", "godaddy.com", "squarespace.com",
    "png.com", "jpg.com" 
}


JUNK_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

def clean_email_data():
    
    Path(PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} raw records from {INPUT_FILE}")
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Run 02_email_extractor.py first.")
        return
        
    
    df.dropna(subset=['Email'], inplace=True)
    
    
    df = df[df['Email'].str.contains(VALID_EMAIL_REGEX, na=False, flags=re.IGNORECASE)]
    
    
    df = df[~df['Email'].str.lower().str.endswith(tuple(JUNK_EXTENSIONS))]

    
    try:
        df['Domain'] = df['Email'].apply(lambda x: x.split('@')[-1].lower())
        df = df[~df['Domain'].isin(JUNK_DOMAINS)]
    except Exception as e:
        print(f"Error processing domains: {e}")

    
    df.drop_duplicates(subset=['Name'], keep='first', inplace=True)
    
    
    final_columns = ['Name', 'Country', 'Email']
    df_final = df[final_columns]
    
    
    df_final.to_csv(OUTPUT_FILE, index=False)
    print(f"--- Cleaning Complete ---")
    print(f"Original: {len(df)} | Cleaned: {len(df_final)}")
    print(f"Saved {len(df_final)} clean, unique records to {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_email_data()