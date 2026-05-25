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
    text = text.replace('&nbsp;', ' ').replace('&#8230;', '...')
    return " ".join(text.split())

def scrape_bisnis(n_pages=20, output_file='bisnis_dataset.csv'):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    base_url = "https://market.bisnis.com/bursa-saham"
    data = []
    seen_urls = set()
    
    print(f"Scraping Bisnis for {n_pages} pages...")
    for page in range(1, n_pages + 1):
        # Using ?p= as a guess for pagination, but loop breaks if duplicates are found
        url = f"{base_url}?p={page}"
        
        try:
            response = scraper.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all article links on the index page
            page_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/read/' in href and href.startswith('http'):
                    page_links.append(href)
            
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
                    date_tag = soup_article.find('div', class_=re.compile('description|date', re.I))
                    if not date_tag:
                        date_tag = soup_article.find(class_='date')
                    date = clean_html_tags(date_tag.text) if date_tag else ""
                    
                    # Extract full text
                    full_text = ""
                    article_tag = soup_article.find('article')
                    if article_tag:
                        # Remove unwanted scripts, styles, or nested divs
                        for unwanted in article_tag(['script', 'style', 'div']):
                            unwanted.extract()
                        full_text = clean_html_tags(article_tag.get_text(separator=' '))
                        
                    teks_gabungan = full_text if full_text else title
                    if not teks_gabungan: continue
                        
                    data.append({'Teks_Gabungan': teks_gabungan, 'Tanggal': date, 'Link': link})
                except Exception as e:
                    print(f"    [Warning] Failed to fetch article {link}: {e}")
                
                time.sleep(1) # Polite delay
                    
            if new_links_found == 0:
                print(f"No new articles found on page {page}, stopping pagination.")
                break
                
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
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    scrape_bisnis(n_pages=50, output_file='bisnis_dataset.csv')
