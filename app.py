import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. NASTAVENÍ A PŘIPOJENÍ ---
st.set_page_config(page_title="Klinické Studie AI", layout="wide", page_icon="🔬")

# Načtení klíče ze Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Použijeme model, který prošel testem
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ API klíč nenalezen! Zkontrolujte nastavení Secrets.")
    st.stop()

# --- 2. FUNKCE PRO NAČTENÍ A PROPOJENÍ DAT ---
@st.cache_data
def load_clinical_data():
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    try:
        # Načtení listů z Excelu
        studie = pd.read_excel(file_name, sheet_name="Studie")
        diagnozy = pd.read_excel(file_name, sheet_name="Diagnozy")
        vazby = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        linie = pd.read_excel(file_name, sheet_name="Linie")
        
        # Propojení tabulek (Merge) - vytvoříme jeden velký kontext pro AI
        # Propojíme ID_Studie, ID_Diagnozy a ID_Linie
        df = vazby.merge(studie, on="ID_Studie", how="left")
        df = df.merge(diagnozy, on="ID_Diagnozy", how="left")
        df = df.merge(linie, on="ID_Linie", how="left")
        
        return studie, df
    except Exception as e:
        st.error(f"❌ Chyba při načítání Excelu: {e}")
        return None, None

df_prehled, df_pro_ai = load_clinical_data()

# --- 3. UŽIVATELSKÉ ROZHRANÍ ---
st.title("🔬 Vyhledávač klinických studií")
st.markdown("Zeptejte se AI na cokoliv z databáze (např. *'Které studie vede Dr. Novák?'* nebo *'Najdi studie pro NSCLC'*).")

if df_pro_ai is not None:
    # Vyhledávací pole
    query = st.text_input("Zadejte svůj dotaz:", placeholder="Hledat...")

    if query:
        with st.spinner("Gemini analyzuje databázi..."):
            try:
                # Výběr klíčových sloupců pro AI, aby nebyl text moc dlouhý
                kontext = df_pro_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Nazev_linie', 'Stav', 'Investigátor', 'Poznamka']].to_string()
                
                prompt = f"""
                Jsi expert na klinické studie. Máš k dispozici tuto databázi:
                {kontext}
                
                Uživatel se ptá: "{query}"
                
                Odpověz česky, stručně a přehledně. 
                Pokud najdeš shodu, uveď název studie, její stav a jméno lékaře (Investigátor).
                """
                
                response = model.generate_content(prompt)
                
                st.subheader("🤖 Odpověď AI")
                st.info(response.text)
                
            except Exception as e:
                st.error(f"Chyba při komunikaci s AI: {e}")

    # Spodní část: Tabulkový přehled jako v AppSheetu
    st.divider()
    st.subheader("📊 Přehled všech studií")
    st.dataframe(df_prehled, use_container_width=True)
else:
    st.warning("Data nebyla načtena. Ujistěte se, že soubor .xlsx je na GitHubu ve stejné složce jako app.py.")
