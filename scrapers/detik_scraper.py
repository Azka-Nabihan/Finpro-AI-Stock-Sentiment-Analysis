import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

def clean_html_tags(text):
    if not text or not isinstance(text, str):
        return ""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    return " ".join(text.split())

def scrape_detik_finance(n_pages=50, output_file='detik_dataset.csv'):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    base_url = "https://finance.detik.com/indeks"
    data = []
    seen_urls = set()
    
    print(f"Scraping Detik Finance for {n_pages} pages...")
    for page in range(1, n_pages + 1):
        url = f"{base_url}?page={page}"
        
        try:
            response = scraper.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('article')
            new_links_found = 0
            
            if not articles:
                print(f"No articles found on page {page}.")
                break
                
            for article in articles:
                try:
                    title_tag = article.find('h3')
                    if not title_tag: continue
                        
                    link_tag = title_tag.find('a')
                    if not link_tag: continue
                        
                    link = link_tag['href']
                    
                    if link in seen_urls:
                        continue
                        
                    seen_urls.add(link)
                    new_links_found += 1
                    
                    title = clean_html_tags(title_tag.text)
                    
                    # Fetch full article text
                    full_text = ""
                    date = ""
                    try:
                        res_article = scraper.get(link, timeout=15)
                        if res_article.status_code == 200:
                            soup_article = BeautifulSoup(res_article.text, 'html.parser')
                            
                            # Extract Date
                            date_tag = soup_article.find('div', class_='detail__date')
                            if date_tag:
                                date = clean_html_tags(date_tag.text)
                            
                            # Extract full text
                            detail_div = soup_article.find('div', class_='detail__body-text')
                            if detail_div:
                                # Remove unwanted embedded links/ads
                                for unwanted in detail_div(['script', 'style', 'div', 'table']):
                                    unwanted.extract()
                                full_text = clean_html_tags(" ".join([p.get_text(separator=' ', strip=True) for p in detail_div.find_all('p', recursive=False)]))
                    except Exception as e:
                        print(f"    [Warning] Failed to fetch full text for {link}: {e}")
                        
                    teks_gabungan = full_text if full_text else title
                    if not teks_gabungan: continue
                        
                    # Clean up prefix like "Jakarta -"
                    teks_gabungan = re.sub(r'(?i)^[\'"]?[A-Z\s]+[-–]\s+', '', teks_gabungan)
                    teks_gabungan = teks_gabungan.strip()
                    
                    data.append({'Teks_Gabungan': teks_gabungan, 'Tanggal': date, 'Link': link})
                    
                except Exception as e:
                    print(f"    [Warning] Skipping an article due to error: {e}")
                    continue
                
                time.sleep(1) # Polite delay
                
            if new_links_found == 0:
                print(f"No new articles found on page {page}, stopping pagination.")
                break
                
            # -- Progressive Saving --
            if data:
                df = pd.DataFrame(data)
                df.insert(0, 'ID', range(1, len(df) + 1))
                df['Label_Sentimen'] = ""
                df = df[['ID', 'Teks_Gabungan', 'Label_Sentimen', 'Tanggal', 'Link']]
                df.to_csv(output_file, sep='|', index=False, encoding='utf-8')
                print(f"Progress saved: {len(data)} articles extracted so far (Page {page}).")
                
        except Exception as e:
            print(f"Error on page {page}: {e}")
            time.sleep(3)
            
    print(f"\nScraping finished. Total extracted: {len(data)}")

if __name__ == "__main__":
    output_path = os.path.join('datasets', 'raw', 'detik_dataset.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scrape_detik_finance(n_pages=50, output_file=output_path)
