# 📈 Klasifikasi Sentimen Berita Finansial Indonesia: TF-IDF + SVM vs IndoBERT

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch&logoColor=white)](#)
[![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface&logoColor=white)](#)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter&logoColor=white)](#)

Proyek ini bertujuan untuk mengklasifikasikan sentimen berita finansial dan saham berbahasa Indonesia ke dalam 3 kelas: **Positif, Netral, dan Negatif**. Proyek ini membandingkan performa model *Machine Learning* tradisional (**TF-IDF + Support Vector Machine**) dengan model *Deep Learning* berbasis Transformer (**IndoBERT**).

## 🗂️ Struktur Direktori dan File

Repositori ini telah dirombak menjadi struktur modular (MLOps) agar lebih mudah dikelola:

```
.
├── scrapers/                         # Kumpulan script scraper berita
│   ├── detik_scraper.py              # Scraper berita saham dari Detik Finance
│   └── kompas_scraper.py             # Scraper berita saham dari Kompas
├── cleaning/                         # Pipeline Pembersihan dan Persiapan Data
│   ├── merge_clean_all.py            # Menggabungkan data manual (Bisnis, IDN, Investor, CNBC) dan hasil scraping
│   └── prepare_training_data.py      # Membersihkan duplikat, dan membagi dataset (Train/Val/Test 80/10/10)
├── datasets/                         # Penyimpanan Dataset
│   ├── raw/                          # Dataset mentah hasil scraping
│   └── processed/                    # Dataset bersih siap latih (train.csv, val.csv, test.csv)
├── Temp/                             # Notebook untuk Latihan Model (Di-run di Google Colab)
│   ├── TF_IDF+SVM_Training (2).ipynb # Pelatihan model baseline SVM (dengan Class Weights)
│   └── Transformer_Training (4).ipynb# Fine-tuning IndoBERT (dengan Layer Freezing & Dropout)
├── datasets_labelling.py             # Script pelabelan otomatis berita menggunakan LLM
├── metadata-progress-report.json     # Laporan progres tugas
└── README.md                         # Dokumentasi proyek
```

---

## 🏗️ Alur Kerja (Pipeline) MLOps

Proyek ini berjalan dalam 4 fase utama:

### 1. 🕷️ Fase Scraping (`scrapers/`)
Berita mentah ditarik secara otomatis menggunakan BeautifulSoup dari berbagai portal berita finansial dan umum utama di Indonesia, yaitu:
- **Bisnis Indonesia** (`bisnis_scraper.py`)
- **Detik Finance** (`detik_scraper.py`)
- **EmitenNews** (`emitennews_scraper.py`)
- **IDN Financials** (`idnfinancials_scraper.py`)
- **Investor.id** (`investor_scraper.py`)
- **Kompas** (`kompas_scraper.py`)

### 2. 🧹 Fase Pengolahan & Penyatuan (`cleaning/merge_clean_all.py`)
Menyatukan seluruh data mentah hasil scraping dengan data manual yang sudah ada, membersihkan formatnya, dan mempersiapkannya untuk tahap pelabelan.

### 3. 🤖 Fase Pelabelan Otomatis (`datasets_labelling.py`)
Sebagian data hasil scraping belum memiliki label sentimen. Script ini menggunakan **API Gemini 3.5 Flash Lite** untuk secara cerdas melabeli berita sebagai "Positif", "Negatif", atau "Netral". Output akhirnya adalah dataset utuh bernama `final_dataset_berlabel.csv`.

### 4. 🗃️ Persiapan & Pembagian Data (`cleaning/prepare_training_data.py`)
Membersihkan data kosong/duplikat dari `final_dataset_berlabel.csv`, lalu mendistribusikan data utuh tersebut menjadi `train.csv` (80%), `val.csv` (10%), dan `test.csv` (10%). Dataset **dibiarkan pada distribusi naturalnya** (imbalanced) untuk mencegah *overfitting* akibat duplikasi teks.

### 5. ⚡ Fase Pelatihan Model (`Temp/`)
Dataset hasil olahan (berada di `datasets/processed/`) diunggah ke Google Colab untuk pelatihan model berat.
- **Model Baseline (SVM)**: Menggunakan ekstraksi fitur TF-IDF. Dioptimasi dengan `GridSearchCV` (`f1_macro`) dan diberi **Class Weights (Balanced)**.
- **Model Utama (IndoBERT)**: Melakukan *fine-tuning* pada `indobenchmark/indobert-base-p1`. Diterapkan teknik **Layer Freezing**, peningkatan **Dropout** (20%), dan **Custom Trainer** dengan **Class Weights**.

---

## 🚀 Cara Menjalankan Secara Berurutan

1. **Jalankan Scraper**: Jalankan script scraper per portal web di folder `scrapers/` (`detik_scraper.py` dan `kompas_scraper.py`) untuk menarik data mentah terbaru.
2. **Gabungkan dan Bersihkan Data**: Jalankan `python cleaning/merge_clean_all.py` untuk menyatukan dan membersihkan hasil scraping beserta data manual lainnya.
3. **Pelabelan AI**: Jalankan `python datasets_labelling.py` untuk melabeli data yang belum berlabel. Hasil akhir dari proses ini akan tersimpan sebagai `datasets/processed/final_dataset_berlabel.csv`.
4. **Siapkan Data Latih**: Jalankan `python cleaning/prepare_training_data.py` untuk memecah dataset final tersebut menjadi `train`, `val`, dan `test`.
5. **Training Model (Cloud/GPU)**: 
   - Unggah folder `datasets/processed/` dan file Notebook dari `Temp/` ke Google Colab.
   - Aktifkan Runtime **T4 GPU**.
   - Sesuaikan `PATH` yang ada di dalam *notebook* lalu jalankan seluruh Cell untuk melakukan *training* dan mendapatkan *Confusion Matrix* akhir.

---

## 👥 Tim Proyek & Kontribusi (Kelompok K14)

*   **Rivi Yasha Hafizhan** (NPM: 230625035) — *MLOps & Pipeline Architecture* 
*   **Azka Nabihan Hilmy** (NPM: 2306250541) — *Data Preprocessing & NLP Pipeline*
*   **M. Arya Wiandra Utomo** (NPM: 2306218295) — *Model Training & Hyperparameter Tuning*
