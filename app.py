import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Konfigurace stránky
st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# 2. Načtení klíče a inicializace AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ Klíč v Secrets chybí! Vložte GEMINI_API_KEY do nastavení.")
    st.stop()

# Funkce, která vyzkouší různé názvy modelů, aby se vyhnula chybě 404
@st.cache_resource
def get_ai_model():
    # Zkusíme tyto 3 varianty názvů (Google je občas mění)
    for model_name in ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-flash-latest"]:
        try:
            m = genai.GenerativeModel(model_name)
            # Testovací dotaz
            m.generate_content("test")
            return m
        except:
            continue
    return None

model = get_ai_model()

if model is None:
    st.error("❌ Chyba 404: Model Gemini nebyl nalezen. Zkuste v nastavení Streamlitu (při mazání a znovu vytvoření appky) změnit Region na 'United States'.")
    st.stop()

# 3. Načtení dat z Excelu
@st.cache_data
def load_data():
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    try:
        # Načtení listů (musí v Excelu existovat!)
        s = pd.read_excel(file_name, sheet_name="Studie")
        v = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        d = pd.read_excel(file_name, sheet_name="Diagnozy")
        l = pd.read_excel(file_name, sheet_name="Linie")
        
        # Propojení dat (Merge)
        full = v.merge(s, on="ID_Studie").merge(d, on="ID_Diagnozy").merge(l, on="ID_Linie")
        return s, full
    except Exception as e:
        st.error(f"❌ Chyba při načítání Excelu: {e}")
        return None, None

df_studie, df_ai_context = load_data()

# 4. Uživatelské rozhraní
st.title("🔬 Vyhledávač klinických studií")

if df_ai_context is not None:
    query = st.text_input("Zadejte dotaz (např. 'Najdi studie pro NSCLC'):")

    if query:
        with st.spinner("AI prohledává databázi..."):
            try:
                # Vytvoření kontextu pro AI
                kontext = df_ai_context[['Nazev_Studie', 'Nazev_Diagnozy', 'Nazev_linie', 'Stav', 'Investigátor']].to_string()
                prompt = f"Data: {kontext}\n\nUživatel: {query}\nOdpověz česky."
                
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"Chyba AI: {e}")

    st.divider()
    st.subheader("📊 Přehled všech studií")
    st.dataframe(df_studie)
