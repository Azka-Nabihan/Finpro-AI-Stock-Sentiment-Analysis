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

def scrape_investor_id(category='market', n_pages=20, output_file='investor_dataset.csv'):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    base_url = f"https://investor.id/{category}/indeks"
    domain = "https://investor.id"
    data = []
    
    print(f"Scraping category '{category}' for {n_pages} pages...")
    for page in range(1, n_pages + 1):
        url = base_url if page == 1 else f"{base_url}/{page}"
        
        try:
            response = scraper.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('div', class_='row mb-4 position-relative')
            if not articles: break
                
            for article in articles:
                try:
                    link_tag = article.find('a', class_='stretched-link')
                    if not link_tag: continue
                    
                    raw_link = link_tag.get('href', '')
                    link = f"{domain}{raw_link}" if raw_link.startswith('/') else raw_link
                    
                    title_tag = article.find('h4')
                    title = clean_html_tags(title_tag.text) if title_tag else ""
                    
                    date_tag = article.find('span', class_='text-muted small')
                    date = clean_html_tags(date_tag.text) if date_tag else ""
                    
                    desc_tag = article.find('span', class_='text-muted text-truncate-2-lines')
                    description = clean_html_tags(desc_tag.text) if desc_tag else ""
                    
                    teks_gabungan = f"{title}. {description}" if description else title
                    data.append({'Teks_Gabungan': teks_gabungan, 'Tanggal': date, 'Link': link})
                except Exception:
                    continue
            time.sleep(2)
            
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
    scrape_investor_id(category='market', n_pages=50, output_file='investor_dataset.csv')
