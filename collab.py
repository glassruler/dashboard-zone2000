import pickle
from pathlib import Path
import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import calendar

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
        dict_df = pd.read_excel('collabreport.xlsx', sheet_name=['dataomzet', 'dataomzet__', 'datagame', 'datach'])
        
        dict_df['dataomzet']["BulanTahun"] = pd.to_datetime(dict_df['dataomzet']["BulanTahun"], errors='coerce')
        dict_df['dataomzet']["month_year"] = dict_df['dataomzet']["BulanTahun"].dt.to_period("M")
        
        dict_df['dataomzet__']["Bulan"] = pd.to_datetime(dict_df['dataomzet__']["Bulan"], format='%m')
        dict_df['dataomzet__']["month_year"] = dict_df['dataomzet__']["Bulan"].dt.to_period("M")
        
        dict_df['datagame']["Order Date"] = pd.to_datetime(dict_df['datagame']["Order Date"], errors='coerce')
        
        return dict_df


    dict_df = load_data()
    dataomzet_df = dict_df['dataomzet']
    dataomzet_new_df = dict_df['dataomzet__']  # New sheet with sales data for comparison
    datagame_df = dict_df['datagame']

    # Sidebar for user filters and logout
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.header("Choose your filter:")

    # Sales Comparison (New Sales Comparison between 2024 and 2025)
    # --- Sales Comparison View (All Locations for Selected Month) ---
    st.divider()
    st.subheader('Sales Comparison: All Locations in a Selected Month (2024 vs. 2025)')

    # Convert to datetime just once if not already done (can be skipped if already parsed)
    dataomzet_new_df['Bulan'] = pd.to_datetime(dataomzet_new_df['Bulan'], errors='coerce')
    
    # Extract month number and name into new columns
    dataomzet_new_df['Month_Num'] = dataomzet_new_df['Bulan'].dt.month
    dataomzet_new_df['Month_Name'] = dataomzet_new_df['Month_Num'].apply(lambda x: calendar.month_name[x])
    
    # Get unique month names for dropdown
    unique_months = dataomzet_new_df['Month_Name'].unique()
    selected_month_name = st.selectbox("Select Month", sorted(unique_months, key=lambda x: list(calendar.month_name).index(x)))
    
    # Filter based on selected month name
    monthly_data = dataomzet_new_df[dataomzet_new_df['Month_Name'] == selected_month_name]
    
    # Pivot safely: group data by location and year
    pivot_df = monthly_data.pivot_table(index='Lokasi', columns='Tahun', values='Total', aggfunc='sum').reset_index()
    pivot_df.columns.name = None
    
    # Ensure both columns exist
    if 2024 not in pivot_df.columns:
        pivot_df[2024] = 0
    if 2025 not in pivot_df.columns:
        pivot_df[2025] = 0
    
    # Rename for consistency
    pivot_df = pivot_df.rename(columns={2024: 'Sales 2024', 2025: 'Sales 2025'})
    
    # Fill NaNs if any
    pivot_df['Sales 2024'] = pivot_df['Sales 2024'].fillna(0)
    pivot_df['Sales 2025'] = pivot_df['Sales 2025'].fillna(0)
    
    # Calculate percentage change safely
    pivot_df['Sales change'] = pivot_df.apply(
        lambda row: f"{((row['Sales 2025'] - row['Sales 2024']) / row['Sales 2024']) * 100:.2f}%" if row['Sales 2024'] != 0 else "N/A",
        axis=1
    )

    
    # Add readable month name to output
    pivot_df.insert(1, 'Bulan', selected_month_name)
    
    # Display table
    st.dataframe(pivot_df)
    
    # Download option
    comparison_csv = pivot_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Monthly Sales Comparison",
        data=comparison_csv,
        file_name=f"Sales_Comparison_{selected_month_name}.csv",
        mime='text/csv'
    )


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

    region = st.sidebar.multiselect("Pick your Branch", filtered_game_df["Center"].unique())
    state = st.sidebar.multiselect("Pick the Game Title", filtered_game_df["GameTitle"].unique())
    city = st.sidebar.multiselect("Pick the Game Code", filtered_game_df["Keterangan"].unique())
    category = st.sidebar.multiselect("Pick the Game Category", filtered_game_df["Category"].dropna().unique())

    def filter_data(df, regions, states, cities, categories):
        if regions:
            df = df[df["Center"].isin(regions)]
        if states:
            df = df[df["GameTitle"].isin(states)]
        if cities:
            df = df[df["Keterangan"].isin(cities)]
        if categories:
            df = df[df["Category"].isin(categories)]
        return df


    filtered_df = filter_data(filtered_game_df, region, state, city, category)

    # Download Button for Raw Filtered Data
    raw_csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="⬇️ Download Raw Filtered Data",
        data=raw_csv,
        file_name="Filtered_Raw_Data.csv",
        mime="text/csv",
        help="Click to download the filtered dataset as CSV"
    )

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

        game_title_df = filtered_df.groupby(["GameTitle", "Category"], as_index=False)["Sales"].sum()
        game_title_df["Sales"] = game_title_df["Sales"].apply(lambda x: f"IDR {x:,.0f}".replace(",", "."))

        # Reorder columns if needed
        game_title_df = game_title_df[["GameTitle", "Category", "Sales"]]

        st.write(game_title_df)

        csv = game_title_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data",
            data=csv,
            file_name="Gametitle.csv",
            mime="text/csv",
            help="Click here to download the data as a CSV file")


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
