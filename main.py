# Packages
import pandas as pd
import numpy as np
from pandas import DataFrame
import datetime
import streamlit as st
import altair as alt
# import ssl
from gspread_pandas import Spread,Client
from google.oauth2 import service_account
import time
from datetime import timedelta
import folium
from streamlit_folium import st_folium




# ssl._create_default_https_context = ssl._create_unverified_context

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
    page_title = "Kenber · Dashboard",
    page_icon = ":bar-chart:",
    initial_sidebar_state = 'auto',
    menu_items = {
        'About' : "# This is a header. This is an *extremely* cool app!"
    })

with open('style.css') as style_css:
    st.markdown(f"<style>{style_css.read()}</style>", unsafe_allow_html = True)


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

def to_altair_datetime(dt):
    dt = pd.to_datetime(dt)
    return alt.DateTime(year=dt.year, month=dt.month, date=dt.day,
                        hours=dt.hour, minutes=dt.minute, seconds=dt.second,
                        milliseconds=0.001 * dt.microsecond)

def text(text):
    st.markdown(text)

def hr():
    st.divider()

def subtext(text):
    st.text(text)

def caption(text):
    st.caption(text)


def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_max = s < 0.5
    return ['background-color: yellow' if v else '' for v in is_max]
 



# df = pd.DataFrame(load_spreadsheet("Work Progress"))
# df_filter = df[df['Country'] == 'Thailand']




# Data Management
date_today = today_date()




df_project = pd.DataFrame(load_spreadsheet("Project"))

df = pd.DataFrame(load_spreadsheet("Work Progress"))

df[['Project ID', 'BOQ Code', 'Item ID']] = df['BOQ ID'].str.split("_", expand = True)

df_boq = pd.DataFrame(load_spreadsheet("BOQ"))

df = df.merge(df_project, on='Project ID', how='left')

df = df.merge(df_boq[['BOQ ID', 'Title', 'Item']], on=["BOQ ID"], how="left")




project_name = str(df['Project Name'].min())






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






if project_selected == "P0" :
   # Dashboard

    # Top Row
    st.title("Dashboard")


    # wch_colour_box = (0,204,102)
    # wch_colour_font = (0,0,0)
    # fontsize = 18
    # valign = "left"
    # iconname = "fas fa-asterisk"
    # sline = "Observations"
    # lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    # i = 123

    # htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
    #                                             {wch_colour_box[1]}, 
    #                                             {wch_colour_box[2]}, 0.75); 
    #                         color: rgb({wch_colour_font[0]}, 
    #                                 {wch_colour_font[1]}, 
    #                                 {wch_colour_font[2]}, 0.75); 
    #                         font-size: {fontsize}px; 
    #                         border-radius: 7px; 
    #                         padding-left: 12px; 
    #                         padding-top: 18px; 
    #                         padding-bottom: 18px; 
    #                         line-height:25px;'>
    #                         <i class='{iconname} fa-xs'></i> {i}
    #                         </style><BR><span style='font-size: 14px; 
    #                         margin-top: 0;'>{sline}</style></span></p>"""

    # st.markdown(lnk + htmlstr, unsafe_allow_html=True)















    # Row A
    st.markdown('### Overall')
    col1, col2, col3, col4 = st.columns((4,2,2,2))

    total_project = df_project['Project ID'].count() - 1
    total_project_finish = df_project['Project ID'][df_project['Overall Status'] == "Finish"].count()
    total_project_ongoing = df_project['Project ID'][df_project['Overall Status'] == "On-Going"].count()
    total_project_unknow = df_project['Project ID'][df_project['Overall Status'] == ""].count() - 1

    col1.metric("Total Project", total_project,"")
    col2.metric("Finish", total_project_finish,"")
    col3.metric("On-Going", total_project_ongoing,"")
    col4.metric("Unknown", total_project_unknow,"")

    hr()


    # Row B
    c1, c2 = st.columns((5,5))
    with c1:
        st.markdown('### Details')

        st.info("Coming Soon")




    with c2:
        st.markdown('### Location')
   
        m = folium.Map(location=[13.736717, 100.523186], zoom_start=5)
        folium.Marker([13.736717, 100.523186], popup="XXXXXX", tooltip="XXXXX",
                    #   icon=folium.DivIcon(
                    #     html="""
                    #     <span>Test</span>
                    #     """
                    #   )
                    ).add_to(m)

        st_folium(m, width='100%', height=420, returned_objects=[])



    hr()    


    # Row C
    st.markdown('### Project Progress')
    success_text = 'background-color:#d9ead3; color:#274e13; font-weight:; text-align:center!important'
    warning_text = 'background-color:#fce8b2; color:#7f6000; font-weight:; text-align:center!important'
    danger_text = 'background-color:#f4c7c3; color:#990000; font-weight:; text-align:center!important'
    info_text = 'background-color:#cfe2f3; color:#0b5394; font-weight:; text-align:center!important'
    unknown_text = 'background-color:#eeeeee;'

    condition_status = lambda x : success_text if x == 'Finish' else (warning_text if x == 'On-Going' else unknown_text)

    table_project = df_project[['Project ID', 'Project Name', 'Start', 'End', 'Overall Status', '%Progress']]
    table_project['Progress (%)'] = np.where(table_project['%Progress'] == "", "", table_project['%Progress'] * 100)
    table_project['Progress (%)'] = pd.to_numeric(table_project['Progress (%)'].replace("", 0))
    # table_project["Progress"] = table_project["Progress"].map('{:.1f}'.format)

    col_table = ['Project ID', 'Project Name', 'Start', 'End', 'Overall Status', 'Progress (%)']
    table_project = table_project[col_table][table_project.index > 0]


    st.table(table_project[col_table].style.applymap(
        condition_status, subset=['Overall Status']).bar(
        subset=['Progress (%)'], color='#b6d7a8', vmin=0, vmax=100).set_precision(1))















if project_selected in list(df['Project ID']):


    # Top Row
    st.title("Dashboard")



    # Row A
    st.markdown('### Details')
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

    newdf = newdf.merge(df_boq, on=['BOQ ID'], how='left')

    newdf["Start Date"] = pd.to_datetime(newdf["Start Date"])

    newdf["End Date"] = pd.to_datetime(newdf["End Date"])

    newdf["Progress_"] = np.concatenate([np.ones(len(newdf)//2), np.zeros(len(newdf)//2), ])

    newdf["Status"] = df['Status']






    start_date_proj = pd.to_datetime(df['Start']).min().date()

    end_date_proj = pd.to_datetime(df['End']).max().date()


    

    newdf['Today'] = date_today

    newdf['Start Project Date'] = pd.to_datetime(start_date_proj)

    newdf['End Project Date'] = pd.to_datetime(end_date_proj)

    newdf["Min Start Date"] = newdf["Start Date"].min().date()

    newdf["Start Date"] = np.where(newdf["Start Date"] == newdf["Min Start Date"], newdf['Start Project Date'], newdf["Start Date"])






    range_ = ['#38761d', '#bcbcbc']



    start_date_domain = start_date_proj - timedelta(days=10)
    end_date_domain = end_date_proj + timedelta(days=10)

    newdf['start_date_domain'] = start_date_domain
    newdf['end_date_domain'] = end_date_domain

    domains = [to_altair_datetime(start_date_domain),
            to_altair_datetime(end_date_domain)]

    date_range = pd.date_range(start=start_date_proj,end=end_date_proj, freq='W-MON')

    newdf["Progress"] = (newdf["Progress (%)"] * 100).map('{:,.0f}'.format).astype(str) + "%"     




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
                axis = alt.Axis(grid=True, labelOverlap=False),
                ),
        tooltip=['Title', 'Item'],
        color=alt.Color('Progress_', scale=alt.Scale(range=range_), legend=None),
    )


    # chart_bar = alt.Chart(newdf).mark_bar(size=30, filled=False, color='black', strokeWidth=0.5).encode(
    #     y=alt.Y("BOQ ID", scale=alt.Scale(padding=0)),
    #     )







    percent_boq = alt.Chart(newdf).mark_text(align='left', baseline='middle', dx=5, color="white", fontWeight="normal").encode(
        y=alt.Y('BOQ ID'),
        x=alt.X('Start Date'),
        text='Progress',
        tooltip=['Title', 'Item'],
    )



    today_date_line = alt.Chart(newdf).mark_rule(color="red").encode(
        x = 'Today',
        tooltip=['Today'],
        size=alt.value(0.5),
    )

    today_date_label = alt.Chart(newdf).mark_text(
        align='center', baseline='bottom', color="red", fontWeight="normal", fontSize=16
    ).encode(
        x=alt.X('Today:T'),
        y = alt.value(0),
        text = 'Today'
    )


    



    start_date_line = alt.Chart(newdf).mark_rule(color='blue').encode(
        x = 'Start Project Date',
        size=alt.value(0.1),
    )
    start_date_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='center', baseline='bottom', color="blue",  fontWeight="normal", fontSize=15).encode(
        x = alt.X('Start Project Date:T'),
        y = alt.value(0),
        text = 'Start Project Date'
    )




    end_date_line = alt.Chart(newdf).mark_rule(color='blue').encode(
        x = 'End Project Date',
        size=alt.value(0.1),
    )
    end_date_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='center', baseline='bottom', color="blue",  fontWeight="normal", fontSize=15).encode(
        x = alt.X('End Project Date:T'),
        y = alt.value(0),
        text = 'End Project Date'
    )





    status_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(align='left', baseline='middle', dx=20, color="black",  fontWeight="normal", fontSize=15).encode(
        y=alt.Y('BOQ ID'),
        x=alt.X('end_date_domain'),
        text='Status',
        tooltip='BOQ ID',
    )








    chart_all = alt.layer(start_date_text, end_date_text, today_date_label, 
                          start_date_line, end_date_line, 
                    
                          chart, percent_boq, today_date_line, status_text)


    st.altair_chart(chart_all, use_container_width=True)








if (not project_selected in list(df['Project ID'])) and (project_selected != "P0"):
    st.warning("Data Not Found")