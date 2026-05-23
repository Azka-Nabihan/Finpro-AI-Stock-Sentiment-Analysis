import pandas as pd
import os
import re

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Menghapus karakter newline (\n, \r) dan menggantinya dengan spasi
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Menghapus karakter unicode yang aneh atau tidak relevan jika ada
    text = text.encode('ascii', 'ignore').decode()
    # Mengganti multiple spasi menjadi single spasi
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def merge_datasets():
    print("Mulai menggabungkan dataset...")
    
    # Path folder dataset
    base_dir = r"c:\Pribadi\Kuliah\Akademis\Semester 6\AI\Finpro"
    raw_dir = os.path.join(base_dir, "datasets", "raw")
    processed_dir = os.path.join(base_dir, "datasets", "processed")
    
    # Pastikan folder processed ada
    os.makedirs(processed_dir, exist_ok=True)
    
    # Daftar file CSV
    files = {
        "CNBC": os.path.join(raw_dir, "cnbc_historical_dataset.csv"),
        "EmitenNews": os.path.join(raw_dir, "emitennews_dataset.csv"),
        "Investor.id": os.path.join(raw_dir, "investor_dataset.csv")
    }
    
    dataframes = []
    
    for sumber, path in files.items():
        if os.path.exists(path):
            try:
                # Membaca CSV (menggunakan separator '|' sesuai yang kita buat)
                df = pd.read_csv(path, sep='|')
                df['Sumber'] = sumber # Tambahkan kolom sumber untuk tracking
                dataframes.append(df)
                print(f"-> Berhasil memuat {len(df)} baris dari {sumber}")
            except Exception as e:
                print(f"-> Gagal memuat {sumber}: {e}")
        else:
            print(f"-> File tidak ditemukan: {path}")
            
    if not dataframes:
        print("Tidak ada data yang bisa digabung!")
        return
        
    # Menggabungkan seluruh dataframe
    gabung_df = pd.concat(dataframes, ignore_index=True)
    total_awal = len(gabung_df)
    
    print(f"\nTotal data awal sebelum dibersihkan: {total_awal} baris")
    
    # Tahap Pembersihan (Cleaning) agar siap dilabeli
    print("Melakukan pembersihan data (Preprocessing dasar)...")
    
    # 1. Bersihkan teks
    gabung_df['Teks_Gabungan'] = gabung_df['Teks_Gabungan'].apply(clean_text)
    
    # 2. Hapus baris yang teksnya kosong
    gabung_df = gabung_df[gabung_df['Teks_Gabungan'] != ""]
    
    # 3. Hapus duplikasi berdasarkan Teks_Gabungan (menghindari berita yang sama terambil 2x)
    gabung_df = gabung_df.drop_duplicates(subset=['Teks_Gabungan'], keep='first')
    
    total_akhir = len(gabung_df)
    print(f"Total data duplikat/kosong yang dihapus: {total_awal - total_akhir} baris")
    print(f"Total data BERSIH akhir: {total_akhir} baris")
    
    # Sesuai permintaan, kita HANYA menyisakan kolom Teks_Gabungan saja
    gabung_df = gabung_df[['Teks_Gabungan']]
    
    # Simpan ke folder processed
    output_path = os.path.join(processed_dir, "dataset_gabungan_siap_label.csv")
    
    try:
        gabung_df.to_csv(output_path, sep='|', index=False, encoding='utf-8')
        print(f"\nSukses! Data gabungan yang bersih disimpan di:\n{output_path}")
    except Exception as e:
        print(f"Gagal menyimpan data gabungan: {e}")

if __name__ == "__main__":
    merge_datasets()
