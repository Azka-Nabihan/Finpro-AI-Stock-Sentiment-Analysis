import pandas as pd
import re
import os

def clean_bisnis(text):
    if not isinstance(text, str):
        return str(text)
    # Remove prefix like "Bisnis.com , JAKARTA — "
    text = re.sub(r'(?i)^[\'"]?Bisnis\.com\s*,\s*[A-Z\s]+[-—–]\s*', '', text)
    # Remove disclaimer at the end
    text = re.sub(r'(?i)_*\s*Disclaimer\s*:.*$', '', text)
    return text.strip()

def clean_investor(text):
    if not isinstance(text, str):
        return str(text)
    # Remove prefix like "JAKARTA, investor.id – "
    text = re.sub(r'(?i)^[\'"]?[A-Z\s]+,\s*investor\.id\s*[-–]\s*', '', text)
    return text.strip()

def clean_idnfinancials(text):
    if not isinstance(text, str):
        return str(text)
    # Remove prefix like "JAKARTA - "
    text = re.sub(r'^[\'"]?[A-Z\s]+[-–]\s+', '', text)
    return text.strip()

def clean_emitennews(text):
    if not isinstance(text, str):
        return str(text)
    # Remove "EmitenNews.com - " at the beginning (case-insensitive)
    cleaned = re.sub(r'(?i)^emitennews\.com\s*-\s*', '', text)
    # Sometimes it might be wrapped in quotes
    cleaned = re.sub(r'(?i)^"emitennews\.com\s*-\s*', '"', cleaned)
    return cleaned.strip()

def clean_detik_kompas(text):
    if not isinstance(text, str):
        return str(text)
    # The scraping scripts for these might have already handled basic prefixes,
    # but we can do a generic cleanup just in case.
    text = re.sub(r'^[\'"]?[A-Z\s]+[-–]\s+', '', text)
    return text.strip()

def main():
    datasets = [
        ('datasets/raw/bisnis_dataset.csv', clean_bisnis),
        ('datasets/raw/investor_dataset.csv', clean_investor),
        ('datasets/raw/idnfinancials_dataset.csv', clean_idnfinancials),
        ('datasets/raw/emitennews_dataset.csv', clean_emitennews),
        ('datasets/raw/detik_dataset.csv', clean_detik_kompas),
        ('datasets/raw/kompas_dataset.csv', clean_detik_kompas)
    ]
    
    all_data = []
    
    for path, func in datasets:
        print(f"Processing {path}...")
        if not os.path.exists(path):
            print(f"Warning: File {path} not found. Skipping...")
            continue
            
        try:
            df = pd.read_csv(path, sep='|', encoding='utf-8')
            if 'Teks_Gabungan' not in df.columns:
                print(f"Warning: 'Teks_Gabungan' column not found in {path}. Skipping...")
                continue
                
            # Clean text
            df['Teks_Gabungan'] = df['Teks_Gabungan'].apply(func)
            
            # Keep only the text column
            df = df[['Teks_Gabungan']]
            all_data.append(df)
            print(f"Successfully processed {len(df)} rows from {path}.")
        except Exception as e:
            print(f"Error processing {path}: {e}")
            
    if not all_data:
        print("No data processed.")
        return
        
    print("Concatenating all datasets...")
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Drop rows with empty or very short text
    final_df.dropna(subset=['Teks_Gabungan'], inplace=True)
    final_df = final_df[final_df['Teks_Gabungan'].str.len() > 10]
    
    # Drop duplicates
    final_df.drop_duplicates(inplace=True)
    
    output_path = 'datasets/scraping_merged_dataset.csv'
    print(f"Saving final dataset ({len(final_df)} rows) to {output_path}...")
    final_df.to_csv(output_path, sep='|', index=False, encoding='utf-8')
    print("Done!")

if __name__ == "__main__":
    main()
