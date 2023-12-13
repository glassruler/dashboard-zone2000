import pickle
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import streamlit_authenticator as stauth

st.set_page_config(page_title="DASH GAME", page_icon=":bar_chart:",layout="wide")

# update login
names = ["Wahyu Hidayat", "Admin Zobu","Roger Tumewu"]
usernames = ["hidayat", "admzobu", "roger"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 
    "collab_report", "abcdef", cookie_expiry_days=10)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Usernames/password is incorrect")

if authentication_status == None:
    st.warning("Please enter username & password")

if authentication_status:
    st.title(" :bar_chart: DASHBOARD REPORT ZONE2000")
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
    st.markdown('<style>.st-emotion-cache-tvhsbf{position: relative; display:block; width:auto;</style>', unsafe_allow_html=True)
    
    #load data frame
    dict_df = pd.read_excel('collabreport.xlsx', 
                       sheet_name=['dataomzet','datagame','datach'])
    
    # Get DataFrame from Dict
    dataomzet_df = dict_df .get('dataomzet')
    datagame_df = dict_df .get('datagame')
    datach_df = dict_df .get('datach')
    
    # colom omzet dan sales by branch
    
    
    
    
    # with view2:
    #     expander = st.expander("Monthly Sales")
    #     data = result
    #     expander.write(data)
    # with dwn2:
    #     st.download_button("Get Data", data = result.to_csv().encode("utf-8"),
    #                        file_name="Monthly Sales.csv", mime="text/csv")
    
    # with view1:
    #     expander = st.expander("Sales by Branch")
    #     data = dataomzet_df[["KodeToko","TotalPenjualan"]].groupby(by="KodeToko")["TotalPenjualan"].sum()
    #     expander.write(data)
    # with dwn1:
    #     st.download_button("Get Data", data = data.to_csv().encode("utf-8"),
    #                        file_name="RetailerSales.csv", mime="text/csv")
    
    
    dataomzet_df["month_year"] = dataomzet_df["BulanTahun"].dt.to_period("M")
    st.subheader('Omzet Zone2000 perbulan (Zone|Kiddieland|Playcafe)')
    
    linechart = pd.DataFrame(dataomzet_df.groupby(dataomzet_df["month_year"].dt.strftime("%Y : %b"))["TotalPenjualan"].sum()).reset_index()
    linechart["TotalPenjualan"] = linechart["TotalPenjualan"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
    
    # fig2 = px.line(linechart, x = "month_year", y="TotalPenjualan", labels = {"TotalPenjualan": "Amount"},height=500, width = 1000,template="gridon")
    # st.plotly_chart(fig2,use_container_width=True)
    
    _, view1, dwn1, view2, dwn2 = st.columns([0.15,0.20,0.20,0.20,0.20])
    with st.expander("Omzet Perbulan Zone2000:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button('Download Data', data = csv, file_name = "TotalPenjualan.csv", mime ='text/csv')
    
    dataomzet_df["Month_Year"] = dataomzet_df["BulanTahun"].dt.strftime("%b'%y")
    result = dataomzet_df.groupby(by = dataomzet_df["Month_Year"])["TotalPenjualan"].sum().reset_index()
    
    
    
    # DASHBOAR GAME TITLE MULAI DISINI    
    st.divider()
    
    st.subheader('Omzet Zone2000 perbulan (Kategori Game)')
    
    col1, col2 = st.columns((2))
    
    datagame_df["Order Date"] = pd.to_datetime(datagame_df["Order Date"])
    
    # Getting the min and max date 
    startDate = pd.to_datetime(datagame_df["Order Date"]).min()
    endDate = pd.to_datetime(datagame_df["Order Date"]).max()
    
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))
    
    datagame_df = datagame_df[(datagame_df["Order Date"] >= date1) & (datagame_df["Order Date"] <= date2)].copy()
    
    # login logout
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    
    st.sidebar.header("Choose your filter: ")
    # Create for Region
    region = st.sidebar.multiselect("Pick your Branch", datagame_df["Center"].unique())
    if not region:
        df2 = datagame_df.copy()
    else:
        df2 = datagame_df[datagame_df["Center"].isin(region)]
    
    # Create for State
    state = st.sidebar.multiselect("Pick the Game Title", df2["GameTitle"].unique())
    if not state:
        df3 = df2.copy()
    else:
        df3 = df2[df2["GameTitle"].isin(state)]
    
    # Create for City
    city = st.sidebar.multiselect("Pick the Game Code",df3["Keterangan"].unique())
    
    # Filter the data based on Region, State and City
    
    if not region and not state and not city:
        filtered_df = datagame_df
    elif not state and not city:
        filtered_df = datagame_df[datagame_df["Center"].isin(region)]
    elif not region and not city:
        filtered_df = datagame_df[datagame_df
        ["GameTitle"].isin(state)]
    elif state and city:
        filtered_df = df3[datagame_df["GameTitle"].isin(state) & df3["Keterangan"].isin(city)]
    elif region and city:
        filtered_df = df3[datagame_df["Center"].isin(region) & df3["Keterangan"].isin(city)]
    elif region and state:
        filtered_df = df3[datagame_df["Center"].isin(region) & df3["GameTitle"].isin(state)]
    elif city:
        filtered_df = df3[df3["Keterangan"].isin(city)]
    else:
        filtered_df = df3[df3["Center"].isin(region) & df3["GameTitle"].isin(state) & df3["Keterangan"].isin(city)]
    
    category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()
    category_df["Sales"] = category_df["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
    
    with st.expander("View Data by Category | Center | Gamtitle:"):
    
            st.write(category_df)
            csv = category_df.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                                help = 'Click here to download the data as a CSV file')
    
            region = filtered_df.groupby(by = "Center", as_index = False)["Sales"].sum()
            region["Sales"] = region["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
      
            st.write(region)
            csv = region.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data", data = csv, file_name = "Cabang.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')
    
    
            region = filtered_df.groupby(by = "GameTitle", as_index = False)["Sales"].sum()
            region["Sales"] = region["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
      
            st.write(region)
            csv = region.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data", data = csv, file_name = "Gametitle.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')
    
    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
    
    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
    linechart["Sales"] = linechart["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))
    
    # fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
    # st.plotly_chart(fig2,use_container_width=True)
    
    with st.expander("View Data of TimeSeries:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

    st.divider()
    st.subheader('Report Pengeluaran Barang CH')

    col1, col2 = st.columns((2))
    

    datach_df["Date"] = pd.to_datetime(datach_df["Date"])

    # Getting the min and max date 
    startDate = pd.to_datetime(datach_df["Date"]).max()
    endDate = pd.to_datetime(datach_df["Date"]).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))

    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    datach_df = datach_df[(datach_df["Date"] >= date1) & (datach_df["Date"] <= date2)].copy()

    toko=st.selectbox("Filter By Toko:",
                            # options=existing_data["NamaToko"] , index=None 
                            options=datach_df["Center"].unique()                          
                            )
    selection_query=datach_df.query(
    "Center== @toko"
    )

    st.dataframe(selection_query)
    "---"
    st.text("Detail Pengeluaran Barang CH By Range Tanggal")
    st.dataframe(datach_df)
    view1, dwn1 = st.columns((2))
    with view1:
        expander = st.expander("Summary Total by Range Tanggal")
        vendor_data = datach_df[["Center","Jumlah"]].groupby(by="Center")["Jumlah"].sum()
        expander.write(vendor_data)
    with dwn1:
        st.download_button("Get Data", data = vendor_data.to_csv().encode("utf-8"),
                           file_name="TotalPengeluaranCH.csv", mime="text/csv")
