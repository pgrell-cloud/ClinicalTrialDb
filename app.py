import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# 1. API Klíč
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Klíč nenalezen v Secrets!")
    st.stop()

# 2. Inicializace modelu s ošetřením chyby 404
@st.cache_resource
def load_ai_model():
    # Zkusíme obě varianty, které Google používá
    for model_name in ['models/gemini-1.5-flash', 'gemini-1.5-flash']:
        try:
            m = genai.GenerativeModel(model_name)
            m.generate_content("test") # Testovací volání
            return m
        except:
            continue
    return None

model = load_ai_model()
if model is None:
    st.error("Chyba: Model Gemini nebyl nalezen (404). Zkuste v Google AI Studiu vytvořit nový klíč.")
    st.stop()

# 3. Načtení dat
@st.cache_data
def load_data():
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    try:
        studie = pd.read_excel(file_name, sheet_name="Studie")
        diagnozy = pd.read_excel(file_name, sheet_name="Diagnozy")
        vazby = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        full = vazby.merge(studie, on="ID_Studie").merge(diagnozy, on="ID_Diagnozy")
        return studie, full
    except Exception as e:
        st.error(f"Chyba dat: {e}")
        return None, None

df_prehled, df_ai = load_data()

# 4. UI
st.title("🔬 Vyhledávač klinických studií")
query = st.text_input("Zadejte dotaz:")

if query and df_ai is not None:
    with st.spinner("Hledám..."):
        try:
            context = df_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Stav', 'Investigátor']].to_string()
            response = model.generate_content(f"Data: {context}\n\nDotaz: {query}\nOdpověz česky.")
            st.info(response.text)
        except Exception as e:
            st.error(f"Chyba AI: {e}")

st.dataframe(df_prehled)
