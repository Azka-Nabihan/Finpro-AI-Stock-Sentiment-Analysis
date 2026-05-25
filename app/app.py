import streamlit as st
import plotly.graph_objects as go
import os
import sys

# Tambahkan direktori models ke path agar bisa import jika diperlukan
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models'))
try:
    from predict import load_svm_model, load_transformer_model, predict_svm, predict_transformer
except ImportError:
    st.error("File models/predict.py tidak ditemukan. Pastikan struktur folder sudah benar.")
    st.stop()

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Prediksi Sentimen Finansial",
    page_icon="📈",
    layout="centered"
)

# Custom CSS untuk mempercantik UI
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1f77b4;
    }
    .subtitle {
        text-align: center;
        color: #555555;
        margin-bottom: 30px;
    }
    .result-box-positif {
        padding: 20px; border-radius: 10px; background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;
        text-align: center; font-size: 24px; font-weight: bold;
    }
    .result-box-negatif {
        padding: 20px; border-radius: 10px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;
        text-align: center; font-size: 24px; font-weight: bold;
    }
    .result-box-netral {
        padding: 20px; border-radius: 10px; background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba;
        text-align: center; font-size: 24px; font-weight: bold;
    }
    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in-section {
        animation: fadeInSlide 0.8s ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📈 Prediksi Sentimen Berita Finansial & Saham</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Bandingkan performa Machine Learning Tradisional (SVM) vs Deep Learning (IndoBERT) secara Real-Time</p>", unsafe_allow_html=True)

# Cache model agar tidak memuat ulang setiap kali tombol diklik
@st.cache_resource(show_spinner=False)
def get_models():
    svm = load_svm_model()
    # Untuk mempercepat loading web jika tidak punya GPU, IndoBERT diload secara opsional
    # Tapi kita akan load saja semuanya karena ini untuk presentasi
    tokenizer, indobert = load_transformer_model()
    return svm, tokenizer, indobert

with st.spinner("🔄 Sedang memuat model AI dari folder lokal... (Mohon tunggu)"):
    svm_model, tokenizer, indobert_model = get_models()

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/color/96/000000/bullish.png", width=80)
st.sidebar.write("### Konfigurasi Model AI")
pilihan_model = st.sidebar.selectbox("Pilih Model AI yang Ingin Digunakan:", ["Transformer (IndoBERT)", "TF-IDF + SVM"])

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.9em; color: gray;'>
<b>Dibuat oleh Kelompok 14:</b><br>
• Rivi Yasha Hafizhan (230625035)<br>
• Azka Nabihan Hilmy (2306250541)<br>
• M. Arya Wiandra Utomo (2306218295)
</div>
""", unsafe_allow_html=True)

# Input UI (Teks Manual atau URL Berita)
tab1, tab2 = st.tabs(["📝 Input Teks Manual", "🔗 Analisis dari URL (Link) Berita"])

# Fungsi bantuan untuk merender hasil
def render_hasil(label, confidence, teks_input, model_name):
    st.write("### Hasil Prediksi:")
    if label == "Positif":
        st.markdown(f"<div class='result-box-positif'>🟢 {label}</div>", unsafe_allow_html=True)
    elif label == "Negatif":
        st.markdown(f"<div class='result-box-negatif'>🔴 {label}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='result-box-netral'>🟡 {label}</div>", unsafe_allow_html=True)
        
    st.write("")
    
    # Render Speedometer (Gauge Chart) menggunakan Plotly
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Confidence Score (%)", 'font': {'size': 20, 'color': 'gray'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#00c389"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ff4b4b'},
                {'range': [50, 80], 'color': '#ffa421'},
                {'range': [80, 100], 'color': '#00c389'}
            ]
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "gray"})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='fade-in-section'>", unsafe_allow_html=True)
    st.write("---")
    st.write("#### ℹ️ Info Detail Analisis")
    st.metric("Panjang Teks", f"{len(teks_input)} Karakter")
    st.write(f"- **Model Digunakan:** {model_name}")
    if "IndoBERT" in model_name:
        st.write("- **Arsitektur:** Transformer (12 Layer, 110M Parameter)")
    else:
        st.write("- **Arsitektur:** Linear Support Vector Classification")
    
    st.write("**Teks yang dianalisis:**")
    with st.container(height=300):
        st.info(teks_input.replace("$", "\\$"))
    st.markdown("</div>", unsafe_allow_html=True)


with tab1:
    st.write("### Masukkan Teks Berita atau Tweet Finansial:")
    teks_manual = st.text_area("Teks Input", height=150, placeholder="Contoh: IHSG ditutup anjlok 2% hari ini...", label_visibility="collapsed")
    
    if st.button("🔍 Analisis Teks Manual", type="primary", use_container_width=True):
        if not teks_manual.strip():
            st.warning("Silakan masukkan teks terlebih dahulu!")
        else:
            with st.spinner("Menganalisis teks..."):
                if "IndoBERT" in pilihan_model:
                    lbl, conf = predict_transformer(teks_manual, tokenizer, indobert_model)
                else:
                    lbl, conf = predict_svm(teks_manual, svm_model)
                # Simpan ke session_state agar tidak hilang
                st.session_state["res_tab1"] = {"label": lbl, "conf": conf, "teks": teks_manual, "model": pilihan_model}
                
    if "res_tab1" in st.session_state:
        r = st.session_state["res_tab1"]
        render_hasil(r["label"], r["conf"], r["teks"], r["model"])

with tab2:
    st.write("### Masukkan Link Berita (Otomatis Scraping):")
    url_input = st.text_input("URL Berita", placeholder="https://news.detik.com/...", label_visibility="collapsed")
    st.info("Sistem akan otomatis mengunduh dan mengekstrak teks berita dari link di atas.")
    
    if st.button("🔍 Analisis dari URL", type="primary", use_container_width=True):
        if not url_input.strip():
            st.warning("Silakan masukkan URL terlebih dahulu!")
        else:
            with st.spinner("⏳ Sedang menyalin teks dari URL..."):
                try:
                    from newspaper import Article
                    artikel = Article(url_input.strip())
                    artikel.download()
                    artikel.parse()
                    teks_url = artikel.text
                    
                    if not teks_url:
                        st.error("Gagal mengekstrak teks dari URL. Mungkin website diblokir atau artikel kosong.")
                    else:
                        st.toast(f"✅ Berhasil menyalin {len(teks_url)} karakter dari link berita tersebut!")
                        with st.spinner("Menganalisis teks..."):
                            if "IndoBERT" in pilihan_model:
                                lbl, conf = predict_transformer(teks_url, tokenizer, indobert_model)
                            else:
                                lbl, conf = predict_svm(teks_url, svm_model)
                            st.session_state["res_tab2"] = {"label": lbl, "conf": conf, "teks": teks_url, "model": pilihan_model}
                except ImportError:
                    st.error("Pustaka 'newspaper3k' belum terinstal.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat mengambil URL: {str(e)}")
                    
    if "res_tab2" in st.session_state:
        r = st.session_state["res_tab2"]
        render_hasil(r["label"], r["conf"], r["teks"], r["model"])
