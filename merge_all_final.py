import pandas as pd

def merge_all():
    cnbci_path = r"c:\Pribadi\Kuliah\Akademis\Semester 6\AI\Finpro\datasets\raw\Dataset-CNBCI-Sentimented.csv"
    self_labeled_path = r"c:\Pribadi\Kuliah\Akademis\Semester 6\AI\Finpro\datasets\processed\dataset_final_berlabel.csv"
    output_path = r"c:\Pribadi\Kuliah\Akademis\Semester 6\AI\Finpro\datasets\processed\dataset_master_sentimen.csv"
    
    print("1. Memuat dataset CNBC Historical (Dataset-CNBCI-Sentimented.csv)...")
    df_cnbci = pd.read_csv(cnbci_path)
    # Filter dan ubah nama kolom
    df_cnbci = df_cnbci[['judul', 'sentimen']].copy()
    df_cnbci.columns = ['Teks', 'Sentimen']
    # Rapikan format sentimen
    df_cnbci['Sentimen'] = df_cnbci['Sentimen'].astype(str).str.strip().str.title()
    print(f"   => Berhasil memuat {len(df_cnbci)} baris.")
    
    print("2. Memuat dataset hasil pelabelan AI sendiri (Gemini)...")
    df_self = pd.read_csv(self_labeled_path, sep='|')
    
    # Filter hanya data yang sudah benar-benar selesai dilabeli
    df_self = df_self.dropna(subset=['Label_Sentimen'])
    df_self = df_self[df_self['Label_Sentimen'].astype(str).str.strip() != ""]
    
    # Samakan format nama kolom
    df_self = df_self.rename(columns={'Teks_Gabungan': 'Teks', 'Label_Sentimen': 'Sentimen'})
    df_self['Sentimen'] = df_self['Sentimen'].astype(str).str.strip().str.title()
    print(f"   => Berhasil mengambil {len(df_self)} baris yang SUDAH berlabel.")
    
    # 3. Menggabungkan
    print("\n3. Menyatukan keduanya menjadi DATASET MASTER...")
    df_master = pd.concat([df_cnbci, df_self[['Teks', 'Sentimen']]], ignore_index=True)
    
    # Hapus baris yang teks atau sentimennya kosong (Pembersihan akhir)
    df_master = df_master.dropna(subset=['Teks', 'Sentimen'])
    
    # Hapus data yang sama persis (Duplikat)
    sebelum_drop = len(df_master)
    df_master = df_master.drop_duplicates()
    sesudah_drop = len(df_master)
    print(f"   => Ditemukan dan dihapus {sebelum_drop - sesudah_drop} baris duplikat.")
    
    # Simpan ke CSV
    df_master.to_csv(output_path, index=False, sep='|')
    print("\n=========================================")
    print("SUKSES MEMBUAT DATASET MASTER (Tanpa IDSMSA)!")
    print(f"Total baris akhir: {len(df_master)} baris data (SIAP UNTUK MACHINE LEARNING)")
    print(f"File tersimpan di: {output_path}")
    print("=========================================")

if __name__ == "__main__":
    merge_all()
