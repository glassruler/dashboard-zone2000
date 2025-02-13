import pickle
from pathlib import Path
import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth

# Page Configuration
st.set_page_config(page_title="DASH GAME", page_icon=":bar_chart:", layout="wide")

# Authentication Setup
names = ["Wahyu Hidayat", "Admin Zobu", "Roger Tumewu"]
usernames = ["hidayat", "admzobu", "roger"]
file_path = Path(__file__).parent / "hashed_pw.pkl"

# Load Hashed Passwords Safely
try:
    with file_path.open("rb") as file:
        hashed_passwords = pickle.load(file)
except (FileNotFoundError, EOFError):
    st.error("Error: Authentication file not found or corrupted.")
    st.stop()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "collab_report", "abcdef", cookie_expiry_days=10)
name, authentication_status, username = authenticator.login("Login", "main")

# Authentication Handling
if authentication_status is False:
    st.error("Usernames/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter username & password")
elif authentication_status:
    st.title(":bar_chart: DASHBOARD REPORT PLAYZONE")
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
    
    # Load Data
    @st.cache_data(ttl=600)
    def load_data():
        dict_df = pd.read_excel('collabreport.xlsx', sheet_name=['dataomzet', 'datagame', 'datach'])
        dict_df['dataomzet']["BulanTahun"] = pd.to_datetime(dict_df['dataomzet']["BulanTahun"], errors='coerce')
        dict_df['dataomzet']["month_year"] = dict_df['dataomzet']["BulanTahun"].dt.to_period("M")
        dict_df['datagame']["Order Date"] = pd.to_datetime(dict_df['datagame']["Order Date"], errors='coerce')
        return dict_df

    dict_df = load_data()
    dataomzet_df = dict_df['dataomzet']
    datagame_df = dict_df['datagame']

    # Omzet Perbulan (Zone|Kiddieland|Playcafe)
    st.subheader('Omzet PLAYZONE perbulan (Zone|Kiddieland|Playcafe)')
    
    @st.cache_data
    def prepare_omzet_data(df):
        df = df.dropna(subset=['TotalPenjualan'])
        linechart = df.groupby(df["month_year"].dt.strftime("%Y : %b"))["TotalPenjualan"].sum().reset_index()
        linechart["TotalPenjualan"] = linechart["TotalPenjualan"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
        return linechart

    linechart = prepare_omzet_data(dataomzet_df)

    with st.expander("Omzet Perbulan PLAYZONE:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button('Download Data', data=csv, file_name="TotalPenjualan.csv", mime='text/csv')

    st.divider()
    
    # Footer
    st.markdown("---")
    st.markdown("Made with Streamlit | Custom by WH")
