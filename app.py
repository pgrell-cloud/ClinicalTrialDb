import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Diagnostika Gemini", layout="wide")

# 1. Kontrola klíče
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("❌ Klíč nenalezen v Secrets!")
    st.stop()

st.title("🔬 Diagnostika připojení k AI")

# 2. Výpis dostupných modelů (TADY ZJISTÍME PRAVDU)
st.subheader("Seznam modelů dostupných pro váš klíč:")
try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            st.write(f"✅ Volatelný model: `{m.name}`")
    
    if not available_models:
        st.warning("⚠️ Váš klíč nevidí žádné modely pro generování textu.")
except Exception as e:
    st.error(f"❌ Chyba při načítání seznamu modelů: {e}")
    st.info("To často znamená, že API klíč je neplatný nebo má špatná oprávnění.")

# 3. Pokus o automatický výběr nejlepšího modelu
st.divider()
if available_models:
    # Hledáme flash, pokud není, vezmeme první dostupný
    selected_model_name = next((m for m in available_models if "flash" in m), available_models[0])
    st.info(f"Zkouším se připojit k: `{selected_model_name}`")
    
    try:
        model = genai.GenerativeModel(selected_model_name)
        test_res = model.generate_content("Ahoj, jsi v pořádku?")
        st.success(f"🤖 AI odpověděla: {test_res.text}")
        
        st.balloons()
        st.write("---")
        st.write("### ✅ Diagnostika úspěšná!")
        st.write(f"V kódu pro aplikaci nyní použijte název: `{selected_model_name}`")
        
    except Exception as e:
        st.error(f"❌ Chyba při testu odpovědi: {e}")
        
