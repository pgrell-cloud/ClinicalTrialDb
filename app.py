import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. NASTAVENÍ AI ---
# Načtení klíče ze Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chybí API klíč v Secrets! Aplikace nemůže fungovat.")
    st.stop()

# DEFINICE MODELU (Tento řádek vám chyběl)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# --- 2. NAČTENÍ DAT ---
@st.cache_data
def load_data():
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx" # Název vašeho souboru
    try:
        # Načtení listů z Excelu
        studie = pd.read_excel(file_name, sheet_name="Studie")
        diagnozy = pd.read_excel(file_name, sheet_name="Diagnozy")
        vazby = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        
        # Propojení dat pro AI
        full_data = vazby.merge(studie, on="ID_Studie", how="left").merge(diagnozy, on="ID_Diagnozy", how="left")
        return studie, full_data
    except Exception as e:
        st.error(f"Chyba při načítání dat: {e}")
        return None, None

df_prehled, df_ai = load_data()

# --- 3. UI A VYHLEDÁVÁNÍ ---
st.title("🔬 Vyhledávač klinických studií")

query = st.text_input("Zadejte dotaz (např. Pembrolizumab nebo Karcinom prsu):")

if query and df_ai is not None:
    with st.spinner("AI přemýšlí..."):
        try:
            # Příprava textu pro AI
            context = df_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Stav', 'Investigátor']].to_string()
            
            prompt = f"Na základě těchto dat:\n{context}\n\nOdpověz na dotaz: {query}. Odpovídej česky."
            
            # VOLÁNÍ MODELU
            response = model.generate_content(prompt)
            
            st.info("Výsledek vyhledávání:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Chyba při komunikaci s AI: {e}")

st.divider()
st.subheader("Celá databáze")
st.dataframe(df_prehled)
