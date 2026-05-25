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

def scrape_emitennews(category='emiten', n_pages=20, output_file='emitennews_dataset.csv'):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    base_url = f"https://www.emitennews.com/category/{category}"
    data = []
    
    print(f"Scraping category '{category}' for {n_pages} pages...")
    for page in range(1, n_pages + 1):
        offset = (page - 1) * 9
        url = f"{base_url}/{offset}" if offset > 0 else base_url
        
        try:
            response = scraper.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('a', class_=re.compile('news-card-2'))
            if not articles: continue
                
            for article in articles:
                try:
                    link = article.get('href', '')
                    if not link: continue
                    
                    title_tag = article.find('p', class_='fs-16')
                    title = clean_html_tags(title_tag.text) if title_tag else ""
                    if not title: continue
                        
                    date_tag = article.find('span', class_='small')
                    date = clean_html_tags(date_tag.text) if date_tag else ""
                    
                    description = ""
                    match_comment = re.search(r'<!--\s*<p>(.*?)</p>\s*-->', str(article))
                    if match_comment:
                        description = clean_html_tags(match_comment.group(1))
                        
                    # Fetch full text from article page
                    full_text = ""
                    try:
                        res_article = scraper.get(link, timeout=15)
                        if res_article.status_code == 200:
                            soup_article = BeautifulSoup(res_article.text, 'html.parser')
                            max_len = 0
                            best_div = None
                            for div in soup_article.find_all('div'):
                                # Find div with the most text inside immediate <p> tags
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

if __name__ == "__main__":
    scrape_emitennews(category="emiten", n_pages=50, output_file="emitennews_dataset.csv")
