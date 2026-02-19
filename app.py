import streamlit as st
import google.generativeai as genai

# Načtení klíče ze Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("API klíč nebyl nalezen v nastavení Secrets!")
    st.stop()

# --- KONFIGURACE ---
st.set_page_config(page_title="Klinické Studie AI", layout="wide", page_icon="🔬")

# Načtení API klíče ze Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ API klíč nenalezen! Přidejte 'GEMINI_API_KEY' do Settings -> Secrets v Dashboardu Streamlitu.")
    st.stop()

# --- NAČTENÍ DAT Z EXCELU ---
@st.cache_data
def load_data():
    # Sem napište přesný název vašeho nahraného souboru na GitHubu
    file_name = "Klinicka_Databaze_3_vzorove_studie.xlsx"
    
    try:
        # Načtení listů (Sheetů)
        studie = pd.read_excel(file_name, sheet_name="Studie")
        diagnozy = pd.read_excel(file_name, sheet_name="Diagnozy")
        vazby = pd.read_excel(file_name, sheet_name="Vazba_Studie")
        linie = pd.read_excel(file_name, sheet_name="Linie")
        
        # Propojení tabulek (stejná logika jako v AppSheetu)
        # Spojíme ID_Studie, ID_Diagnozy a ID_Linie do jednoho přehledu
        data = vazby.merge(studie, on="ID_Studie", how="left")
        data = data.merge(diagnozy, on="ID_Diagnozy", how="left")
        data = data.merge(linie, on="ID_Linie", how="left")
        
        return studie, data
    except Exception as e:
        st.error(f"❌ Chyba při načítání Excelu: {e}")
        return None, None

df_prehled, df_pro_ai = load_data()

# --- HLAVNÍ ROZHRANÍ ---
st.title("🔬 Vyhledávač klinických studií")
st.markdown("Zadejte dotaz v přirozené řeči (např. *'Jaké studie máme pro NSCLC v 1. linii?'*)")

if df_pro_ai is not None:
    query = st.text_input("Vyhledat v databázi:", placeholder="Např. Pembrolizumab, Karcinom prsu, Dr. Novák...")

    if query:
        with st.spinner("Gemini analyzuje data..."):
            try:
                # Použití konkrétní verze modelu pro opravu chyby InvalidArgument
                model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                
                # Příprava kontextu pro AI
                context = df_pro_ai[['Nazev_Studie', 'Nazev_Diagnozy', 'Nazev_linie', 'Stav', 'Investigátor', 'Poznamka']].to_string()
                
                prompt = f"""
                Jsi odborný asistent pro klinické studie. 
                Zde jsou data z naší databáze:
                {context}
                
                Uživatel se ptá: {query}
                
                Odpověz česky, stručně a přehledně. Uveď název studie, stav náboru a jméno lékaře (Investigátor).
                Pokud v datech nic takového není, řekni to.
                """
                
                response = model.generate_content(prompt)
                
                st.subheader("🤖 Odpověď AI")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Chyba AI: {e}")
                st.info("Tip: Zkontrolujte, zda je váš API klíč aktivní v Google AI Studiu.")

    # Zobrazení tabulky na spodu (jako v AppSheetu)
    st.divider()
    st.subheader("📊 Přehled všech studií")
    st.dataframe(df_prehled, use_container_width=True)
    
