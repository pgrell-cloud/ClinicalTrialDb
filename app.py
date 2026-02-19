import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- NASTAVENÍ GEMINI ---
# Zde vložte svůj klíč, nebo ho v Streamlit Cloud vložte do "Secrets"
API_KEY = "VÁŠ_API_KLÍČ" 
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Klinické Studie", layout="wide")

# --- FUNKCE PRO NAČTENÍ DAT ---
@st.cache_data
def load_and_merge_data():
    # Načtení vašich CSV souborů
    studie = pd.read_csv("Klinicka_Databaze_3_vzorove_studie.xlsx - Studie.csv")
    diagnozy = pd.read_csv("Klinicka_Databaze_3_vzorove_studie.xlsx - Diagnozy.csv")
    vazby = pd.read_csv("Klinicka_Databaze_3_vzorove_studie.xlsx - Vazba_Studie.csv")
    linie = pd.read_csv("Klinicka_Databaze_3_vzorove_studie.xlsx - Linie.csv")
    
    # Propojení tabulek pro AI kontext
    m = vazby.merge(studie, on="ID_Studie").merge(diagnozy, on="ID_Diagnozy").merge(linie, on="ID_Linie")
    return studie, m

try:
    df_display, df_context = load_and_merge_data()
    
    st.title("🔬 Vyhledávač klinických studií")
    
    query = st.text_input("Zadejte dotaz (např. 'Najdi studie pro NSCLC v 1. linii'):")

    if query:
        with st.spinner("Gemini hledá v databázi..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Vytvoření textového popisu dat pro AI
            data_str = df_context[['Nazev_Studie', 'Nazev_Diagnozy', 'Nazev_linie', 'Stav', 'Investigátor', 'Poznamka']].to_string()
            
            prompt = f"Na základě těchto dat o klinických studiích:\n\n{data_str}\n\nOdpověz na dotaz: {query}. Odpovídej česky a stručně."
            
            response = model.generate_content(prompt)
            st.info("Výsledek od AI:")
            st.write(response.text)

    st.divider()
    st.subheader("Tabulkový přehled")
    st.dataframe(df_display)

except Exception as e:
    st.error(f"Nepodařilo se načíst data. Ujistěte se, že jsou CSV soubory ve stejné složce. Chyba: {e}")