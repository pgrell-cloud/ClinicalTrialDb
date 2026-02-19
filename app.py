import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. ZÁKLADNÍ NASTAVENÍ ---
st.set_page_config(page_title="Klinické Studie AI", layout="wide")

# Načtení klíče ze Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ API klíč nenalezen v Secrets!")
    st.stop()

# --- 2. OPRAVA CHYBY 404 (HLEDÁNÍ SPRÁVNÉHO NÁZVU MODELU) ---
@st.cache_resource
def get_model():
    # Vyzkoušíme nejdříve standardní název, pak verzi s cestou
    model_names = ['gemini-1.5-flash', 'models/gemini-1.5-flash']
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            # Zkusíme krátký test, zda model reaguje
            model.generate_content("test") 
            return model
        except Exception:
            continue
    return None

model = get_model()

if model is None:
    st.error("❌ Nepodařilo se inicializovat AI model. Zkontrolujte API klíč nebo region.")
    st.stop()

# --- 3. NAČTENÍ DAT Z EXCELU ---
@st.cache_data
def load_data():
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    try:
        # Načtení listů (přesně podle vašich názvů)
        df_studie = pd.read_excel(file_name, sheet_name="Studie")
        df_diagnozy = pd.read_excel(file_name, sheet_name="Diagnozy")
        df_vazby = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        
        # Propojení tabulek
        full_data = df_vazby.merge(df_studie, on="ID_Studie", how="left").merge(df_diagnozy, on="ID_Diagnozy", how="left")
        return df_studie, full_data
    except Exception as e:
        st.error(f"❌ Chyba při načítání Excelu: {e}")
        return None, None

df_prehled, df_ai = load_data()

# --- 4. UI A VYHLEDÁVÁNÍ ---
st.title("🔬 Vyhledávač klinických studií")

if df_ai is not None:
    query = st.text_input("Zadejte dotaz (např. 'Pembrolizumab'):")

    if query:
        with st.spinner("AI hledá..."):
            try:
                # Sestavení textového kontextu pro AI
                context = df_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Stav', 'Investigátor']].to_string()
                
                prompt = f"Na základě těchto dat o studiích:\n{context}\n\nOdpověz na dotaz: {query}. Odpovídej česky."
                
                response = model.generate_content(prompt)
                st.success("Odpověď AI:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Chyba při komunikaci: {e}")

    st.divider()
    st.subheader("📊 Přehled databáze")
    st.dataframe(df_prehled)
