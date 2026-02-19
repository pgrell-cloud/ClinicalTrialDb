import streamlit as st
import pandas as pd
import google.generativeai as genai

# Konfigurace
st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# Inicializace klíče
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Klíč v Secrets chybí!")
    st.stop()

# FUNKCE PRO PŘIPOJENÍ - Zkoušíme různé verze API, abychom obešli 404
@st.cache_resource
def load_stable_model():
    # Seznam všech možných názvů, které Google akceptuje
    test_names = [
        "models/gemini-1.5-flash",
        "gemini-1.5-flash",
        "models/gemini-pro"
    ]
    
    for name in test_names:
        try:
            model = genai.GenerativeModel(name)
            # Testovací mikro-dotaz
            model.generate_content("Hi", generation_config={"max_output_tokens": 1})
            return model
        except Exception:
            continue
    return None

model = load_stable_model()

if model is None:
    st.error("⚠️ AI model stále hlásí chybu 404. Zkuste v Google AI Studiu vytvořit ÚPLNĚ NOVÝ API KLÍČ (tlačítko 'Create API key in new project'). Staré klíče někdy v nových regionech nefungují.")
    st.stop()

# Načtení dat
@st.cache_data
def load_data():
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    try:
        s = pd.read_excel(file_name, sheet_name="Studie")
        v = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        d = pd.read_excel(file_name, sheet_name="Diagnozy")
        merged = v.merge(s, on="ID_Studie").merge(d, on="ID_Diagnozy")
        return s, merged
    except Exception as e:
        st.error(f"Chyba dat: {e}")
        return None, None

df_s, df_ai = load_data()

st.title("🔬 Vyhledávač klinických studií")

query = st.text_input("Zadejte dotaz:")
if query and df_ai is not None:
    with st.spinner("Hledám..."):
        try:
            context = df_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Stav']].to_string()
            response = model.generate_content(f"Data: {context}\n\nDotaz: {query}\nOdpověz česky.")
            st.info(response.text)
        except Exception as e:
            st.error(f"Chyba AI: {e}")

if df_s is not None:
    st.dataframe(df_s)
    
