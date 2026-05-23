import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def clean_html_tags(text):
    if not text or not isinstance(text, str):
        return ""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    return " ".join(text.split())

def scrape_cnbc_market_indeks(n_pages=50, output_file='cnbc_historical_dataset.csv'):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    base_url = "https://www.cnbcindonesia.com/market/indeks/5"
    data = []
    
    print(f"Scraping {n_pages} pages...")
    for page in range(1, n_pages + 1):
        url = f"{base_url}?page={page}"
        try:
            response = scraper.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('article')
            if not articles:
                articles = soup.find_all('li')
            if not articles:
                continue

            for article in articles:
                try:
                    a_tag = article.find('a')
                    link = a_tag['href'] if a_tag and 'href' in a_tag.attrs else ""
                    if not link: continue
                    
                    title_tag = article.find(['h2', 'h3'])
                    title = clean_html_tags(title_tag.text) if title_tag else ""
                    if not title: continue
                        
                    date_tag = article.find(class_=re.compile('date|time'))
                    date = clean_html_tags(date_tag.text) if date_tag else ""
                    
                    desc_tag = article.find(class_=re.compile('subjudul|desc|summary|detail_text'))
                    description = clean_html_tags(desc_tag.text) if desc_tag else ""
                    
                    teks_gabungan = f"{title}. {description}" if description else title
                    data.append({'Teks_Gabungan': teks_gabungan, 'Tanggal': date, 'Link': link})
                except Exception:
                    continue
            time.sleep(2.5)
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            time.sleep(3)
            
    print(f"Total extracted: {len(data)}")
    if not data: return
        
    df = pd.DataFrame(data)
    df.insert(0, 'ID', range(1, len(df) + 1))
    df['Label_Sentimen'] = ""
    df = df[['ID', 'Teks_Gabungan', 'Label_Sentimen', 'Tanggal', 'Link']]
    df.to_csv(output_file, sep='|', index=False, encoding='utf-8')

if __name__ == "__main__":
    scrape_cnbc_market_indeks(n_pages=50, output_file="cnbc_historical_dataset.csv")
