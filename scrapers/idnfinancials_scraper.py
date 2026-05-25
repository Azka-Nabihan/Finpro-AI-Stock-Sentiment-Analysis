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

def scrape_idnfinancials(n_pages=20, output_file='idnfinancials_dataset.csv'):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    base_url = "https://www.idnfinancials.com/id/news"
    data = []
    
    print(f"Scraping IDNFinancials for {n_pages} pages...")
    for page in range(1, n_pages + 1):
        url = base_url if page == 1 else f"{base_url}/page/{page}"
        
        try:
            response = scraper.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            headers = soup.find_all(['h2', 'h3'], class_='title')
            if not headers: break
                
            for h in headers:
                try:
                    a_tag = h.find('a')
                    if not a_tag: continue
                    link = a_tag.get('href', '')
                    if not link: continue
                    
                    title = clean_html_tags(a_tag.text)
                    
                    container = h.parent
                    date_tag = container.find('p', class_='date-published')
                    date = clean_html_tags(date_tag.text) if date_tag else ""
                    
                    desc_tag = container.find('p', class_='summary')
                    description = clean_html_tags(desc_tag.text) if desc_tag else ""
                    
                    # Fetch full text from article page
                    full_text = ""
                    try:
                        res_article = scraper.get(link, timeout=15)
                        if res_article.status_code == 200:
                            soup_article = BeautifulSoup(res_article.text, 'html.parser')
                            max_len = 0
                            best_div = None
                            for div in soup_article.find_all('div'):
                                text = " ".join([p.get_text(separator=' ', strip=True) for p in div.find_all('p', recursive=False)])
                                if len(text) > max_len:
                                    max_len = len(text)
                                    best_div = div
                            
                            if best_div:
                                full_text = clean_html_tags(" ".join([p.get_text(separator=' ', strip=True) for p in best_div.find_all('p', recursive=False)]))
                    except Exception as e:
                        print(f"    [Warning] Failed to fetch full text for {link}: {e}")
                    
                    teks_gabungan = full_text if full_text else (f"{title}. {description}" if description else title)
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
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    scrape_idnfinancials(n_pages=50, output_file='idnfinancials_dataset.csv')
