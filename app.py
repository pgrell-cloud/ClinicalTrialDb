import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Nastavení stránky a AI
st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# Načtení klíče ze Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ API klíč nenalezen v Secrets!")
    st.stop()

# 2. Funkce pro načtení dat
@st.cache_data
def load_data():
    # Název souboru musí přesně odpovídat tomu na GitHubu
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    try:
        # Načtení listů (používáme knihovnu pandas přes zkratku pd)
        df_studie = pd.read_excel(file_name, sheet_name="Studie")
        df_diagnozy = pd.read_excel(file_name, sheet_name="Diagnozy")
        df_vazby = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        df_linie = pd.read_excel(file_name, sheet_name="Linie")
        
        # Propojení tabulek do jedné velké (tzv. Flat Table)
        full_data = df_vazby.merge(df_studie, on="ID_Studie", how="left")
        full_data = full_data.merge(df_diagnozy, on="ID_Diagnozy", how="left")
        full_data = full_data.merge(df_linie, on="ID_Linie", how="left")
        
        return df_studie, full_data
    except Exception as e:
        st.error(f"❌ Chyba při načítání Excelu: {e}")
        return None, None

# Spuštění načítání
df_display, df_context = load_data()

# 3. Uživatelské rozhraní
st.title("🔬 Vyhledávač klinických studií")

if df_display is not None:
    query = st.text_input("Zadejte dotaz (např. 'Pembrolizumab' nebo 'studie pro melanom'):")

    if query:
        with st.spinner("Gemini prohledává vaši databázi..."):
            try:
                # Výběr sloupců, které posíláme AI, aby to nebylo moc dlouhé
                context_text = df_context[['Nazev_Studie', 'Nazev_Diagnozy', 'Nazev_linie', 'Stav', 'Investigátor', 'Poznamka']].to_string()
                
                prompt = f"Máš k dispozici tyto klinické studie:\n{context_text}\n\nUživatel se ptá: {query}\nOdpověz česky a stručně."
                
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"Chyba AI: {e}")

    # Zobrazení tabulky pod vyhledáváním
    st.divider()
    st.subheader("📊 Kompletní seznam studií")
    st.dataframe(df_display, use_container_width=True)
