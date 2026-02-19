import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- KONFIGURACE ---
st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# Načtení API klíče
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ API klíč nenalezen v Secrets!")
    st.stop()

# Definice modelu - opravený název pro verzi v1beta
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('models/gemini-1.5-flash')

# --- NAČTENÍ DAT ---
@st.cache_data
def load_data():
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    try:
        # Načtení listů z Excelu pomocí pandas (pd)
        studie = pd.read_excel(file_name, sheet_name="Studie")
        diagnozy = pd.read_excel(file_name, sheet_name="Diagnozy")
        vazby = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        
        # Propojení dat (Join)
        full_data = vazby.merge(studie, on="ID_Studie", how="left").merge(diagnozy, on="ID_Diagnozy", how="left")
        return studie, full_data
    except Exception as e:
        st.error(f"❌ Chyba při načítání dat: {e}")
        return None, None

df_prehled, df_ai = load_data()

# --- UI ---
st.title("🔬 Vyhledávač klinických studií")

if df_ai is not None:
    query = st.text_input("Zadejte dotaz (např. Pembrolizumab):")

    if query:
        with st.spinner("AI hledá v databázi..."):
            try:
                # Omezení kontextu pro AI
                context = df_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Stav', 'Investigátor']].to_string()
                prompt = f"Data ze studií:\n{context}\n\nUživatel hledá: {query}\nOdpověz česky."
                
                response = model.generate_content(prompt)
                st.success("Výsledek:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Chyba AI: {e}")

    st.divider()
    st.dataframe(df_prehled)
    
