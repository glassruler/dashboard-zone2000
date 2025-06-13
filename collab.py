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

with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "collab_report", "abcdef", cookie_expiry_days=10)
name, authentication_status, username = authenticator.login("Login", "main")

# Authentication Handling
if authentication_status == False:
    st.error("Usernames/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter username & password")
elif authentication_status:
    st.title(":bar_chart: DASHBOARD REPORT PLAYZONE")
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
    st.markdown('<style>.st-emotion-cache-tvhsbf{position: relative; display:block; width:auto;</style>', unsafe_allow_html=True)

    # Load Data
    @st.cache_data(ttl=600)  # Refresh cache every 10 minutes
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
        linechart = df.groupby(df["month_year"].dt.strftime("%Y : %b"))["TotalPenjualan"].sum().reset_index()
        linechart["TotalPenjualan"] = linechart["TotalPenjualan"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
        return linechart

    linechart = prepare_omzet_data(dataomzet_df)

    with st.expander("Omzet Perbulan PLAYZONE:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button('Download Data', data=csv, file_name="TotalPenjualan.csv", mime='text/csv')

    # Omzet Perbulan (Kategori Game)
    st.divider()
    st.subheader('Omzet PLAYZONE perbulan (Kategori Game)')

    col1, col2 = st.columns(2)
    startDate = datagame_df["Order Date"].min()
    endDate = datagame_df["Order Date"].max()

    with col1:
        date1 = st.date_input("Start Date", startDate)
    with col2:
        date2 = st.date_input("End Date", endDate)

    date1 = pd.to_datetime(date1)
    date2 = pd.to_datetime(date2)

    filtered_game_df = datagame_df[(datagame_df["Order Date"] >= date1) & (datagame_df["Order Date"] <= date2)]

    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.header("Choose your filter:")

    region = st.sidebar.multiselect("Pick your Branch", filtered_game_df["Center"].unique())
    state = st.sidebar.multiselect("Pick the Game Title", filtered_game_df["GameTitle"].unique())
    city = st.sidebar.multiselect("Pick the Game Code", filtered_game_df["Keterangan"].unique())

    def filter_data(df, regions, states, cities):
        if regions:
            df = df[df["Center"].isin(regions)]
        if states:
            df = df[df["GameTitle"].isin(states)]
        if cities:
            df = df[df["Keterangan"].isin(cities)]
        return df

    filtered_df = filter_data(filtered_game_df, region, state, city)

    category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
    category_df["Sales"] = category_df["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))

    with st.expander("View Data by Category | Center | Gamtitle:"):
        st.write(category_df)
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        region_df = filtered_df.groupby("Center", as_index=False)["Sales"].sum()
        region_df["Sales"] = region_df["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
        st.write(region_df)
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Cabang.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        game_title_df = filtered_df.groupby("GameTitle", as_index=False)["Sales"].sum()
        game_title_df["Sales"] = game_title_df["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
        st.write(game_title_df)
        csv = game_title_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Gametitle.csv", mime="text/csv", help='Click here to download the data as a CSV file')

    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")

    @st.cache_data
    def prepare_timeseries_data(df):
        linechart = df.groupby(df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum().reset_index()
        linechart["Sales"] = linechart["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
        return linechart

    linechart = prepare_timeseries_data(filtered_df)

    with st.expander("View Data of TimeSeries:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

    st.divider()
