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

def scrape_kompas(n_pages=50, output_file='kompas_dataset.csv'):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    base_url = "https://www.kompas.com/tag/saham"
    data = []
    seen_urls = set()
    
    print(f"Scraping Kompas for {n_pages} pages...")
    for page in range(1, n_pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        
        try:
            response = scraper.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links that look like an article
            page_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/read/' in href and 'kompas.com' in href:
                    # Remove query params from url if any
                    clean_href = href.split('?')[0]
                    page_links.append(clean_href)
            
            new_links_found = 0
            for link in set(page_links):
                if link in seen_urls:
                    continue
                    
                seen_urls.add(link)
                new_links_found += 1
                
                try:
                    res_article = scraper.get(link, timeout=15)
                    if res_article.status_code != 200: continue
                        
                    soup_article = BeautifulSoup(res_article.text, 'html.parser')
                    
                    # Extract title
                    title_tag = soup_article.find('h1')
                    title = clean_html_tags(title_tag.text) if title_tag else ""
                    
                    # Extract date
                    date_tag = soup_article.find('div', class_='read__time')
                    date = clean_html_tags(date_tag.text) if date_tag else ""
                    
                    # Extract full text
                    full_text = ""
                    content_div = soup_article.find('div', class_='read__content')
                    if content_div:
                        # Find all p tags within the content div
                        paragraphs = content_div.find_all('p')
                        full_text = " ".join([p.get_text(separator=' ', strip=True) for p in paragraphs])
                        full_text = clean_html_tags(full_text)
                    
                    teks_gabungan = full_text if full_text else title
                    if not teks_gabungan: continue
                        
                    # Clean up prefix like "JAKARTA, KOMPAS.com -"
                    teks_gabungan = re.sub(r'(?i)^[\'"]?[A-Z\s]+,\s*KOMPAS\.com\s*[-–]\s+', '', teks_gabungan)
                    teks_gabungan = re.sub(r'(?i)^[\'"]?[A-Z\s]+[-–]\s+', '', teks_gabungan)
                    teks_gabungan = teks_gabungan.strip()
                    
                    data.append({'Teks_Gabungan': teks_gabungan, 'Tanggal': date, 'Link': link})
                    
                except Exception as e:
                    print(f"    [Warning] Failed to fetch article {link}: {e}")
                    
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
    output_path = os.path.join('datasets', 'raw', 'kompas_dataset.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scrape_kompas(n_pages=50, output_file=output_path)
