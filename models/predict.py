import argparse
import sys
import os
import numpy as np

# Konfigurasi Label
LABEL_MAP = {0: "Negatif", 1: "Netral", 2: "Positif"}

# Dapatkan direktori tempat script ini berada (folder models)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_svm_model(model_path=os.path.join(BASE_DIR, "svm_model", "svm_model.joblib")):
    print("[INFO] Memuat model TF-IDF + SVM...")
    try:
        import joblib
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        print(f"[ERROR] File model SVM tidak ditemukan di '{model_path}'!")
        sys.exit(1)
    except ImportError:
        print("[ERROR] Pustaka scikit-learn tidak terinstal. Jalankan: pip install scikit-learn")
        sys.exit(1)

def load_transformer_model(model_path=os.path.join(BASE_DIR, "indobert-finetuned")):
    print("[INFO] Memuat model IndoBERT (ini mungkin memakan waktu sebentar)...")
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        # Gunakan CPU untuk prediksi lokal agar kompatibel di semua PC
        model.eval()
        return tokenizer, model
    except OSError:
        print(f"[ERROR] Folder model IndoBERT tidak ditemukan di '{model_path}'!")
        print("Silakan download folder 'indobert-finetuned' dari Google Drive Anda dan taruh di folder 'models/'.")
        sys.exit(1)
    except ImportError:
        print("[ERROR] Pustaka transformers/torch tidak terinstal. Jalankan: pip install transformers torch")
        sys.exit(1)

def predict_svm(text, model):
    # SVM dalam pipeline sklearn (TfidfVectorizer + LinearSVC)
    # LinearSVC tidak memiliki predict_proba secara bawaan, 
    # namun kita bisa menggunakan decision_function untuk mengestimasi confidence
    pred = model.predict([text])[0]
    
    # Estimasi persentase keyakinan menggunakan decision_function
    decision = model.decision_function([text])[0]
    # Normalisasi menggunakan softmax manual untuk mendapatkan probabilitas pseudo
    exp_decision = np.exp(decision - np.max(decision))
    probabilities = exp_decision / exp_decision.sum()
    
    confidence = np.max(probabilities) * 100
    
    return LABEL_MAP[pred], confidence

def predict_transformer(text, tokenizer, model):
    import torch
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        # Hitung probabilitas dengan softmax
        probabilities = torch.nn.functional.softmax(logits, dim=-1)[0].numpy()
        
        pred_idx = np.argmax(probabilities)
        confidence = probabilities[pred_idx] * 100
        
        return LABEL_MAP[pred_idx], confidence

def main():
    print("="*50)
    print("📈 AI Prediksi Sentimen Saham & Finansial 📈")
    print("="*50)
    
    print("Pilih model yang ingin digunakan:")
    print("1. TF-IDF + SVM (Cepat & Ringan)")
    print("2. IndoBERT (Akurat & Mendalam)")
    
    pilihan = input("Masukkan angka (1/2): ").strip()
    
    if pilihan == '1':
        model = load_svm_model()
        model_type = "SVM"
    elif pilihan == '2':
        tokenizer, model = load_transformer_model()
        model_type = "Transformer"
    else:
        print("Pilihan tidak valid.")
        sys.exit(1)
        
    print(f"\n[OK] Berhasil memuat model {model_type}!")
    
    while True:
        print("-" * 50)
        teks = input("\nMasukkan teks berita/saham (atau ketik 'keluar' untuk berhenti):\n> ")
        if teks.lower() in ['keluar', 'exit', 'quit']:
            break
            
        if not teks.strip():
            continue
            
        print("\nMenganalisis...")
        
        if model_type == "SVM":
            label, confidence = predict_svm(teks, model)
        else:
            label, confidence = predict_transformer(teks, tokenizer, model)
            
        # Pewarnaan teks output untuk terminal (opsional)
        warna = ""
        reset = "\033[0m"
        if label == "Positif": warna = "\033[92m" # Hijau
        elif label == "Negatif": warna = "\033[91m" # Merah
        elif label == "Netral": warna = "\033[93m" # Kuning
            
        print(f"Hasil Sentimen : {warna}{label}{reset}")
        print(f"Tingkat Yakin  : {confidence:.2f}%")

if __name__ == "__main__":
    main()
