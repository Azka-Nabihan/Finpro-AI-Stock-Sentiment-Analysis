import pandas as pd
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

# Muat rahasia dari file .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("API Key tidak ditemukan! Pastikan file .env ada dan berisi GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

def get_sentiment_batch(texts):
    """Fungsi untuk mengirim BANYAK teks ke Gemini sekaligus"""
    
    # Merakit kumpulan teks menjadi 1 string dengan penomoran
    kumpulan_teks = ""
    for i, teks in enumerate(texts):
        kumpulan_teks += f"Teks {i+1}: {teks}\n"
        
    prompt = f"""
    Kamu adalah ahli keuangan pasar modal. Tugasmu menganalisis sentimen {len(texts)} berita saham.
    Kamu HANYA boleh menjawab dengan {len(texts)} baris kata. 
    Setiap baris HANYA boleh berisi 1 kata: POSITIF, NEGATIF, atau NETRAL.
    Jangan berikan penjelasan apapun. Pastikan jumlah jawabanmu pas {len(texts)} baris.
    
    Kumpulan Berita:
    {kumpulan_teks}
    
    Jawaban:
    """
    
    try:
        response = model.generate_content(prompt)
        raw_labels = response.text.strip().split('\n')
    
        clean_labels = []
        for label in raw_labels:
            bersih = label.upper().replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '').replace('7.', '').replace('8.', '').replace('9.', '').replace('10.', '').replace('-', '').strip()
            
            if "POSITIF" in bersih:
                clean_labels.append("Positif")
            elif "NEGATIF" in bersih:
                clean_labels.append("Negatif")
            elif "NETRAL" in bersih:
                clean_labels.append("Netral")
            else:
                clean_labels.append("Netral") 
                
        # Jika AI berhalusinasi dan memberikan jawaban kurang dari jumlah teks, penuhi sisanya dengan kosong
        while len(clean_labels) < len(texts):
            clean_labels.append("")
            
        return clean_labels[:len(texts)] # Pastikan jumlahnya pas tidak kelebihan
            
    except Exception as e:
        print(f"\n   [!] Error API: {e}")
        return [""] * len(texts) # Jika error, semua dikosongkan agar bisa diulangi nanti

def run_labeling_batch():
    input_path = r"c:\Pribadi\Kuliah\Akademis\Semester 6\AI\Finpro\datasets\scraping_merged_dataset.csv"
    output_path = r"c:\Pribadi\Kuliah\Akademis\Semester 6\AI\Finpro\datasets\final_dataset_berlabel.csv"
    
    if os.path.exists(output_path):
        print("Mendeteksi file progres... Melanjutkan pelabelan BATCH...")
        df = pd.read_csv(output_path, sep='|')
    else:
        print("Memulai pelabelan BATCH dari awal (Semua Data)...")
        df = pd.read_csv(input_path, sep='|')
        
    if 'Label_Sentimen' not in df.columns:
        df['Label_Sentimen'] = ""
    df['Label_Sentimen'] = df['Label_Sentimen'].astype('object')

    
    BATCH_SIZE = 15
    total_baris = len(df)
    print(f"Total data: {total_baris} baris (Akan diproses per {BATCH_SIZE} data)")
    
    batch_texts = []
    batch_indices = []
    
    for index, row in df.iterrows():
        # Jika belum dilabeli
        if pd.isna(row['Label_Sentimen']) or str(row['Label_Sentimen']).strip() == "":
            batch_texts.append(row['Teks_Gabungan'])
            batch_indices.append(index)
            
        # Jika keranjang batch sudah penuh (15), Kumpulkan dan kirim ke AI
        if len(batch_texts) == BATCH_SIZE or (index == total_baris - 1 and len(batch_texts) > 0):
            print(f"Menganalisis Batch baris ke {batch_indices[0]+1} s/d {batch_indices[-1]+1}...")
            
            hasil_batch = get_sentiment_batch(batch_texts)
            
            # Memasukkan hasil ke dalam dataframe
            for i, idx in enumerate(batch_indices):
                df.at[idx, 'Label_Sentimen'] = hasil_batch[i]
                
            # Simpan progres
            df.to_csv(output_path, sep='|', index=False)
            
            # Kosongkan keranjang untuk data 15 berikutnya
            batch_texts = []
            batch_indices = []
            
            # Jeda
            time.sleep(3) 
            
    print("\nPROSES PELABELAN BATCH SELESAI 100%!")
    print(f"Hasil disimpan di: {output_path}")

if __name__ == "__main__":
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "PASTE_API_KEY_ANDA_DI_SINI":
        print("Masukkan API Key Anda di baris ke-7 atau di file .env")
    else:
        run_labeling_batch()
