import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter

sns.set(style='dark')

def create_byMonth_df(df):

	byMontlyCasual_df = df.groupby(by=["year","mnth","month"]).agg({
	    "casual": "sum"
	}).sort_values(by=["year","mnth"]).reset_index()
	byMontlyCasual_df["user_type"] = "Casual"
	byMontlyCasual_df["monthYear"] = byMontlyCasual_df['month'].astype(str) +' '+ byMontlyCasual_df['year'].astype(str)

	byMontlyCasual_df.rename(columns={
	    "casual": "total_user"
	}, inplace=True)

	byMontlyRegistered_df = df.groupby(by=["year","mnth","month"]).agg({
	    "registered": "sum"
	}).sort_values(by=["year","mnth"]).reset_index()
	byMontlyRegistered_df["user_type"] = "Registered"
	byMontlyRegistered_df["monthYear"] = byMontlyRegistered_df['month'].astype(str) +' '+ byMontlyRegistered_df['year'].astype(str)

	byMontlyRegistered_df.rename(columns={
	    "registered": "total_user"
	}, inplace=True)

	merge_df = pd.concat([byMontlyCasual_df, byMontlyRegistered_df])
	filtered_df = merge_df.groupby(by=["user_type","year","mnth","monthYear"]).agg({
	    "total_user": "sum"
	}).sort_values(by=["user_type","year","mnth"]).reset_index()
    
	return filtered_df

def create_bySeason_df(df):

    filtered_df = df.groupby(by=["season","seasonStr"]).agg({
        "casual": "mean",
        "registered" : "mean",
        "cnt" : "mean"
    }).sort_values(by="season").reset_index()
    
    return filtered_df

def create_byWorkingday_df(df):

    filtered_df = df.query("holiday==0").groupby(by=["weekday","dayName"]).agg({
        "casual": "mean",
        "registered" : "mean",
        "cnt" : "mean"
    }).sort_values(by="weekday").reset_index()
    
    return filtered_df

def create_byHourly_df(df):

    filtered_df = df.groupby(by=["hr"]).agg({
        "casual": "mean",
        "registered" : "mean",
        "cnt" : "mean"
    }).sort_values(by="hr").reset_index()
    
    return filtered_df



daily_df = pd.read_csv("rent_day_df.csv")
hourly_df = pd.read_csv("rent_hour_df.csv")

daily_df["dteday"] = pd.to_datetime(daily_df["dteday"])

min_date = daily_df["dteday"].min()
max_date = daily_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan

    st.image("indraCycle.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

sorted_daily_df = daily_df[(daily_df["dteday"] >= str(start_date)) & 
                (daily_df["dteday"] <= str(end_date))]
sorted_hourly_df = hourly_df[(hourly_df["dteday"] >= str(start_date)) & 
                (hourly_df["dteday"] <= str(end_date))]

byMonth_df = create_byMonth_df(sorted_daily_df)
bySeason_df = create_bySeason_df(sorted_daily_df)
byWorkingday_df = create_byWorkingday_df(sorted_daily_df)
byHourly_df = create_byHourly_df(sorted_hourly_df)

st.header('Bike Rental Data Analytics')

st.subheader('Monthly Rental')
 
col1, col2 = st.columns(2)
 
with col1:
    total_rent_casual = sorted_daily_df.casual.sum()
    st.metric("Total Casual Rent", value=f'{total_rent_casual:,}')
 
with col2:
    # total_rent_registered = format_currency(sorted_daily_df.registered.sum(), "AUD", locale='es_CO') 
    total_rent_registered = sorted_daily_df.registered.sum()
    st.metric("Total Registered Rent", value=f'{total_rent_registered:,}')


sns.set_style("whitegrid")

fig, ax = plt.subplots(figsize=(16, 10))
sns.barplot(
    y="total_user", 
    x="monthYear",
    hue="user_type",
    data=byMonth_df.sort_values(by=["year","mnth"]),
    palette=["#72BCD4","#FA8937"],
    ax=ax
)

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
st.pyplot(fig)

st.markdown("***")

st.subheader('Average Seasonal Rental')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 10))
sns.barplot(
    y="casual", 
    x="seasonStr",
    hue="seasonStr",
    data=bySeason_df.sort_values(by="season"),
    palette=["#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3"],
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Total Casual User by Season", loc="center", fontsize=25)
ax[0].tick_params(axis ='y', labelsize=25)
ax[0].tick_params(axis ='x', labelsize=25)
ax[0].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
for container in ax[0].containers:
    ax[0].bar_label(container, fmt='%.2f')

sns.barplot(
    y="registered", 
    x="seasonStr",
    hue="seasonStr",
    data=bySeason_df.sort_values(by="season"),
    palette=["#D3D3D3", "#D3D3D3", "#FA8937", "#D3D3D3"],
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Total Registered User by Season", loc="center", fontsize=25)
ax[1].tick_params(axis ='y', labelsize=25)
ax[1].tick_params(axis ='x', labelsize=25)
ax[1].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
for container in ax[1].containers:
    ax[1].bar_label(container, fmt='%.2f')
st.pyplot(fig)

bySeason_df.rename(columns={
    "seasonStr": "Season Name",
    "casual": "Casual Rental",
    "registered" : "Registered Rental"
}, inplace=True)
st.dataframe(data=bySeason_df[["Season Name","Casual Rental","Registered Rental"]], use_container_width =True)


st.markdown("***")

st.subheader('Average Daily Rental')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

ax[0].plot(byWorkingday_df["dayName"], byWorkingday_df["casual"], marker='o', linewidth=2, color="#72BCD4")
ax[0].set_title("Total Casual User Per Day", loc="center", fontsize=25)
ax[0].tick_params(axis ='y', labelsize=25)
ax[0].tick_params(axis ='x', labelsize=22, rotation=30)
ax[0].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

ax[1].plot(byWorkingday_df["dayName"], byWorkingday_df["registered"], marker='o', linewidth=2, color="#FA8937")
ax[1].set_title("Total Registered User Per Day", loc="center", fontsize=25) 
ax[1].tick_params(axis ='y', labelsize=25)
ax[1].tick_params(axis ='x', labelsize=22, rotation=30)
ax[1].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
st.pyplot(fig)

byWorkingday_df.rename(columns={
    "dayName": "Day",
    "casual": "Casual Rental",
    "registered" : "Registered Rental"
}, inplace=True)
st.dataframe(data=byWorkingday_df[["Day","Casual Rental","Registered Rental"]], use_container_width =True)


st.markdown("***")

st.subheader('Average Hourly Rental')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
ax[0].plot(byHourly_df["hr"], byHourly_df["casual"], marker='o', linewidth=2, color="#72BCD4")
ax[0].set_title("Total Casual User Per Hour", loc="center", fontsize=25)
ax[0].tick_params(axis ='y', labelsize=25)
ax[0].tick_params(axis ='x', labelsize=22, rotation=30)
ax[0].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

ax[1].plot(byHourly_df["hr"], byHourly_df["registered"], marker='o', linewidth=2, color="#FA8937")
ax[1].set_title("Total Registered User Per Hour", loc="center", fontsize=25) 
ax[1].tick_params(axis ='y', labelsize=25)
ax[1].tick_params(axis ='x', labelsize=22, rotation=30)
ax[1].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

plt.suptitle("Average User by Hour", fontsize=30)
st.pyplot(fig)

byHourly_df.rename(columns={
    "hr": "Hour",
    "casual": "Casual Rental",
    "registered" : "Registered Rental"
}, inplace=True)
st.dataframe(data=byHourly_df[["Hour","Casual Rental","Registered Rental"]], use_container_width =True)