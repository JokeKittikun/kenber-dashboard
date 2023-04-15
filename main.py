# Packages
import pandas as pd
import numpy as np
from pandas import DataFrame
import datetime
import streamlit as st
import altair as alt
import ssl
from gspread_pandas import Spread,Client
from google.oauth2 import service_account
import time
from datetime import timedelta
import folium
from streamlit_folium import st_folium

ssl._create_default_https_context = ssl._create_unverified_context

# Create a Google Authentication Connect Object
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes = scope)
client = Client(scope = scope, creds = credentials)
spreadsheetname = "Database"
spread = Spread(spreadsheetname, client = client)



# Set Page Config
st.set_page_config(layout = 'wide',
    page_title = "Dashboard",
    page_icon = "🧊",
    initial_sidebar_state = 'auto',
    menu_items = {
        'About' : "# This is a header. This is an *extremely* cool app!"
    })



# Functions
# Get our Worksheet names
sh = client.open(spreadsheetname)
worksheet_list = sh.worksheets()

# Get our Worksheet names
def worksheet_names():
    sheet_names = []
    for sheet in worksheet_list:
        sheet_names.append(sheet.title)
    return sheet_names

# Get the Sheet as Dataframe
def load_spreadsheet(spreadsheetname):
    worksheet = sh.worksheet(spreadsheetname)
    df = DataFrame(worksheet.get_all_records())
    return df


def today_date():
    date = datetime.datetime.now().date()
    return date
date_today = today_date()


def to_altair_datetime(dt):
    dt = pd.to_datetime(dt)
    return alt.DateTime(year=dt.year, month=dt.month, date=dt.day,
                        hours=dt.hour, minutes=dt.minute, seconds=dt.second,
                        milliseconds=0.001 * dt.microsecond)

# df = pd.DataFrame(load_spreadsheet("Work Progress"))
# df_filter = df[df['Country'] == 'Thailand']




# Data Management
mapObj = folium.Map(location=[21,21])

df_project = pd.DataFrame(load_spreadsheet("Project"))

df = pd.DataFrame(load_spreadsheet("Work Progress"))

df[['Project ID', 'BOQ Code', 'Item ID']] = df['BOQ ID'].str.split("_", expand = True)

df = df.merge(df_project, on='Project ID', how='left')

project_name = str(df['Project Name'].min())





# Map
st.header('Header :blue[colors] Text :sunglasses:')
st.subheader('Subheader :blue[colors] Text :sunglasses:')
st.markdown("# Markdown 1")
st.markdown("## Markdown 2")
st.markdown("### Markdown 3")
st.markdown("#### Markdown 4")
st.markdown("##### Markdown 5")
st.markdown("###### Markdown 6")
st.text("Text")
st.caption('Caption')

st.divider()




m = folium.Map(location=[13.736717, 100.523186], zoom_start=5)
folium.Marker([13.736717, 100.523186], popup="XXXXXX", tooltip="XXXXX",
            #   icon=folium.DivIcon(
            #     html="""
            #     <span>Test</span>
            #     """
            #   )
              ).add_to(m)

st_folium(m, width='100%', height=500, returned_objects=[])



# Data Visualization

# Sliderbar
st.sidebar.header('Dashboard `Test version`')
st.sidebar.subheader('Project Selection')

project_selection = st.sidebar.selectbox(
    'Project Name',
    (df_project['Project ID'] + " - " + df_project['Project Name']))
project_selected = project_selection.split(" - ", 1)[0]


st.sidebar.markdown('''
---
Created by [Joke Kittikun](#).
''')



# Data Filter
df = df[df['Project ID'] == project_selected]

if project_selected in list(df['Project ID']):


    # Dashboard

    st.write(date_today)
    # Top Row
    st.title("Dashboard")



    # Row A
    st.markdown('### Metrics')
    col1, col2, col3 = st.columns((6,2,2))
    col1.metric("Project Name", project_name,"")
    col2.metric("Province", "Bangkok","")
    col3.metric("Overall Progress", "P1","")

    # Row B
    c1, c2 = st.columns((6,4))
    with c1:
        st.markdown('### Area 1')

    with c2:
        st.markdown('### Area 2')

    # Row C
    st.markdown('### Area 3')







    df["Start Date"] = pd.to_datetime(df["Start Date"])
    df["End Date"] = pd.to_datetime(df["End Date"])

    df["Progress Date"] =  (df["End Date"] - df["Start Date"]) * df["Progress (%)"] + df["Start Date"]


    newdf = np.concatenate([df[["BOQ ID", "Start Date", "End Date", "Progress (%)"]].values,  
                            df[["BOQ ID", "Start Date", "Progress Date", "Progress (%)"]].values])

    newdf = pd.DataFrame(newdf, columns=["BOQ ID", "Start Date", "End Date", "Progress (%)"])

    newdf["Start Date"] = pd.to_datetime(newdf["Start Date"])

    newdf["End Date"] = pd.to_datetime(newdf["End Date"])

    newdf["Progress_"] = np.concatenate([np.ones(len(newdf)//2), np.zeros(len(newdf)//2), ])

    newdf["Status"] = df['Status']

    start_date = newdf['Start Date'].min().date()

    end_date = newdf['End Date'].max().date()

    newdf['today'] = date_today
    newdf['start_date_project'] = start_date
    newdf['end_date_project'] = end_date

    range_ = ['#38761d', '#bcbcbc']



    start_date_domain = start_date - timedelta(days=7)
    end_date_domain = end_date + timedelta(days=7)
    newdf['start_date_domain'] = start_date_domain
    newdf['end_date_domain'] = end_date_domain

    domains = [to_altair_datetime(start_date_domain),
            to_altair_datetime(end_date_domain)]

    date_range = pd.date_range(start=start_date,end=end_date, freq='W-MON')

            



    chart = alt.Chart(newdf).mark_bar(cornerRadius=3).encode(
        x=alt.X('Start Date',
                axis = alt.Axis(grid=True, title="", labelOverlap=True, labelAngle=0, orient="bottom",
                                gridOpacity=0.85,
                                offset=-10,
                                ),
                scale = alt.Scale(domain=domains)
                ),
        x2='End Date',
        y=alt.Y('BOQ ID',
                axis = alt.Axis(grid=True,labelOverlap=False),
                ),
        tooltip='BOQ ID',
        color=alt.Color('Progress_', scale=alt.Scale(range=range_), legend=None),
    )


    # chart_bar = alt.Chart(newdf).mark_bar(size=30, filled=False, color='black', strokeWidth=0.5).encode(
    #     y=alt.Y("BOQ ID", scale=alt.Scale(padding=0)),
    #     )





    newdf["Progress"] = (newdf["Progress (%)"] * 100).map('{:,.0f}'.format).astype(str) + "%"

    percent_boq = alt.Chart(newdf).mark_text(align='left', baseline='middle', dx=5, color="white", fontWeight="normal").encode(
        y=alt.Y('BOQ ID'),
        x=alt.X('Start Date'),
        text='Progress',
        tooltip='BOQ ID',
    )



    today_date_line = alt.Chart(newdf).mark_rule(color="orange").encode(
        x = 'today',
        tooltip=['today'],
        size=alt.value(2),
    )

    today_date_label = alt.Chart(newdf).mark_text(
        align='center', baseline='bottom', color="orange", fontWeight="normal", fontSize=16
    ).encode(
        x=alt.X('today:T', aggregate={'argmax': 'today'}),
        y = alt.value(0),
        text = 'today'
    )






    start_date_line = alt.Chart(newdf).mark_rule(color='blue').encode(
        x = 'start_date_project',
    )

    end_date_line = alt.Chart(newdf).mark_rule(color='blue').encode(
        x = 'end_date_project',
    )


    status_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(align='left', baseline='middle', dx=20, color="black",  fontWeight="normal", fontSize=15).encode(
        y=alt.Y('BOQ ID'),
        x=alt.X('end_date_domain'),
        text='Status',
        tooltip='BOQ ID',
    )

    start_date_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='right', baseline='middle', dx=-2, color="gray",  fontWeight="normal", fontSize=11).encode(
        y=alt.Y('BOQ ID'),
        x=alt.X('Start Date'),
        text='Start Date'
        # text='End Date',
    )

    end_date_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='left', baseline='middle', dx=2, color="gray",  fontWeight="normal", fontSize=11).encode(
        y=alt.Y('BOQ ID'),
        x=alt.X('End Date'),
        text='End Date'
        # text='End Date',
    )




    chart_all = alt.layer(start_date_text, end_date_text, today_date_line, today_date_label, 
                    start_date_line, 
                    end_date_line, chart, percent_boq, status_text)


    st.altair_chart(chart_all, use_container_width=True)