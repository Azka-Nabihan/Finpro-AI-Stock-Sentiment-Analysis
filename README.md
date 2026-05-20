# 📈 Klasifikasi Sentimen Berita Finansial Indonesia: TF-IDF + SVM vs IndoBERT

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch&logoColor=white)](#)
[![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface&logoColor=white)](#)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter&logoColor=white)](#)

Proyek ini membandingkan performa model klasifikasi tradisional **TF-IDF + Support Vector Machine (SVM)** dengan model pemelajaran mendalam berbasis *Transformer* **IndoBERT** (`indobenchmark/indobert-base-p1`) untuk analisis sentimen teks finansial berbahasa Indonesia. 

Data yang digunakan merupakan gabungan dari tweet finansial (**ID-SMSA**) dan berita portal **CNBC Indonesia**, yang diklasifikasikan ke dalam 3 kelas sentimen mikro: **Positif, Netral, dan Negatif**.

---

## 🏗️ Arsitektur MLOps (Pemisahan Notebook)

Untuk menghindari kendala memori (*CUDA Out of Memory*) dan memisahkan tugas komputasi secara modular, repositori ini dibagi menjadi dua modul utama:

```
.
├── IDSMSA.csv                         # Dataset tweet finansial dari Twitter/X
├── Dataset-CNBCI-Sentimented.csv      # Dataset judul berita dari CNBC Indonesia
├── dataset_gabungan_final.csv         # Dataset bersih hasil pemrosesan Notebook 1
├── Data_Pipeline_Preprocessing.ipynb  # [Notebook 1] Pipeline ETL (CPU)
├── Model_Training_and_Evaluation.ipynb# [Notebook 2] Training & Evaluasi Model (GPU)
├── metadata-progress-report.json      # Laporan progress & deklarasi kontribusi
└── README.md                          # Dokumentasi proyek
```

### 1. 🧹 `Data_Pipeline_Preprocessing.ipynb` (Fase ETL)
*   **Fokus**: Pembersihan teks (*case folding*, penghapusan karakter khusus, standardisasi) dan penyelarasan label sentimen.
*   **Kebutuhan Runtime**: CPU Standar.
*   **Output**: Menghasilkan berkas gabungan terstandardisasi `dataset_gabungan_final.csv` untuk siap latih.

### 2. ⚡ `Model_Training_and_Evaluation.ipynb` (Fase Komputasi GPU)
*   **Fokus**: Pemisahan data latih-uji (80:20), pembuatan model baseline, dan proses *fine-tuning* IndoBERT.
*   **Teknik Optimasi**: Penggunaan **FP16 Mixed Precision** dan **Batch Size = 16** untuk optimasi memori GPU T4.
*   **Kebutuhan Runtime**: GPU (misalnya NVIDIA T4 di Google Colab).
*   **Output**: Laporan metrik evaluasi (Akurasi, Presisi, Recall, F1-Score) dan *Confusion Matrix*.

---

## 🚀 Cara Menjalankan

### Cara Cepat (Google Colab / Cloud GPU)
1. Unggah berkas `Data_Pipeline_Preprocessing.ipynb`, `IDSMSA.csv`, dan `Dataset-CNBCI-Sentimented.csv` ke lingkungan Google Colab.
2. Jalankan seluruh sel pada **Notebook 1** (ETL) untuk menghasilkan berkas `dataset_gabungan_final.csv`.
3. Buka **Notebook 2** (`Model_Training_and_Evaluation.ipynb`), aktifkan akselerator **T4 GPU** di pengaturan Runtime Google Colab.
4. Jalankan seluruh sel pada **Notebook 2** untuk melatih baseline model dan model IndoBERT secara aman dari *Out of Memory*.

### Instalasi Lokal
Jika ingin menjalankan secara lokal, pastikan Anda menggunakan virtual environment (`.venv`) dan pasang pustaka yang diperlukan:

```bash
# Clone repositori
git clone https://github.com/Azka-Nabihan/Finpro-AI-Stock-Sentiment-Analysis.git
cd Finpro-AI-Stock-Sentiment-Analysis

# Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # Untuk Linux/macOS
.venv\Scripts\activate     # Untuk Windows (Powershell)

# Pasang pustaka utama
pip install pandas scikit-learn transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 👥 Tim Proyek & Kontribusi (Kelompok K00)

*   **Rivi Yasha Hafizhan** (NPM: 230625035) — *Data Preprocessing & NLP Pipeline*
*   **Azka Nabihan Hilmy** (NPM: 2306250541) — *MLOps & Pipeline Architecture*
*   **M. Arya Wiandra Utomo** (NPM: 2306218295) — *Model Training & Hyperparameter Tuning*
