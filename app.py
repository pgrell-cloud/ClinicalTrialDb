import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- NASTAVENÍ TAJNÉHO KLÍČE ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chybí API klíč v Secrets!")
    st.stop()

st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# --- FUNKCE PRO NAČTENÍ DAT Z EXCELU ---
@st.cache_data
def load_data():
    # ZDE ZMĚŇTE NÁZEV NA VÁŠ SKUTEČNÝ SOUBOR
    file_path = "Klinicka_Databaze_3_vzorove_studie.xlsx" 
    
    try:
        # Načítáme jednotlivé listy (Sheet names)
        df_studie = pd.read_excel(file_path, sheet_name="Studie")
        df_diagnozy = pd.read_excel(file_path, sheet_name="Diagnozy")
        df_vazby = pd.read_excel(file_path, sheet_name="Vazba_Studie")
        df_linie = pd.read_excel(file_path, sheet_name="Linie")
        
        # Propojení tabulek pro AI (stejné jako u CSV)
        full_context = df_vazby.merge(df_studie, on="ID_Studie", how="left")
        full_context = full_context.merge(df_diagnozy, on="ID_Diagnozy", how="left")
        full_context = full_context.merge(df_linie, on="ID_Linie", how="left")
        
        return df_studie, full_context
    except Exception as e:
        st.error(f"Chyba při načítání Excelu: {e}")
        return None, None

df_display, df_ai = load_data()

if df_display is not None:
    st.title("🔬 Smart Vyhledávač (Excel Verze)")
    
    query = st.text_input("Co hledáte?")
    
    if query:
        with st.spinner("Gemini čte listy Excelu..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Převod dat na text pro AI
            context_text = df_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Nazev_linie', 'Stav', 'Investigátor']].to_string()
            
            prompt = f"Data: {context_text}\n\nDotaz: {query}\n\nOdpověz česky."
            response = model.generate_content(prompt)
            st.info(response.text)

    st.divider()
    st.dataframe(df_display)
    
