# Packages
import pandas as pd
import numpy as np
from pandas import DataFrame
import datetime
import streamlit as st
import altair as alt
import ssl
# import gspread
from gspread_pandas import Spread,Client
from google.oauth2 import service_account

import time
from datetime import timedelta
import folium
from streamlit_folium import st_folium
from PIL import Image



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
    page_title = "Kenber · Dashboard",
    page_icon = ":bar-chart:",
    initial_sidebar_state = 'auto',
    menu_items = {
        'About' : "# This is a header. This is an *extremely* cool app!"
    })

with open('style.css') as style_css:
    st.markdown('<style>' + style_css.read() + '</style>', unsafe_allow_html=True)


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

df = df.merge(df_boq[['BOQ ID', 'Title', 'Item', 'Unit']], on=["BOQ ID"], how="left")


project_name = str(df['Project Name'].min())
project_province = str(df['Province'].min())
project_country = str(df['Country'].min())

df_cal = df[df['Status'].notnull()]








# Data Visualization

# Sliderbar

image_logo = Image.open('img/Kenber Logo.png')

st.sidebar.image(image_logo)


st.sidebar.header('Dashboard `Test version`')
# st.sidebar.subheader('Project Selection')

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

overall_status =  df_project[df_project['Project ID'] == project_selected]['Overall Status'].values[0]
overall_progress = str(df_project[df_project['Project ID'] == project_selected]['%Progress'].values[0] * 100) + "%"
remaining_days = df_project[df_project['Project ID'] == project_selected]['Remaining Days'].values[0]





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

        total_project_value = pd.to_numeric(df_project['Project Value']).sum()
        st.metric("Total Project Value", "{:,.2f}".format(total_project_value),"")

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
    unknown_text = 'background-color:#eeeeee; color:#eeeeee;'

    condition_status = lambda x : success_text if x == 'Finish' else (warning_text if x == 'On-Going' else unknown_text)
    condition_remaining_days = lambda x : info_text if x > 0 else (unknown_text if np.isnan(x) else danger_text)

    table_project = df_project[['Project ID', 'Project Name','BOQ Type', 'Start', 'End', 'Remaining Days', 'Overall Status', '%Progress']]
    table_project['Progress (%)'] = np.where(table_project['%Progress'] == "", "", table_project['%Progress'] * 100)
    table_project['Progress (%)'] = pd.to_numeric(table_project['Progress (%)'].replace("", 0))

    table_project['Remaining Days'] = pd.to_numeric(table_project['Remaining Days'])
    # table_project["Progress"] = table_project["Progress"].map('{:.1f}'.format)

    col_table = ['Project ID', 'Project Name', 'BOQ Type', 'Start', 'End', 'Remaining Days', 'Overall Status', 'Progress (%)']
    table_project = table_project[col_table][table_project.index > 0]

    tb = table_project[col_table].style.applymap(
            condition_status, subset=['Overall Status']).bar(
            subset=['Progress (%)'], color='#b6d7a8', vmin=0, vmax=100)
    tb2 = tb.applymap(condition_remaining_days, subset=['Remaining Days']).set_precision(0)

    st.table(tb2)















if project_selected in list(df['Project ID']):


    # Top Row
    st.title("Dashboard")



    # Row A
    col1, col2 = st.columns((5,5))
    with col1:
        st.markdown('### Details')
        st.metric("Project Name", project_name,"")

        sub_c1, sub_c2 = col1.columns((1,1))
        with sub_c1:    
            st.metric("Province", project_province,"")
        with sub_c2:  
            st.metric("Country", project_country,"")

        m = folium.Map(location=[13.736717, 100.523186], zoom_start=5)
        folium.Marker([13.736717, 100.523186], popup="XXXXXX", tooltip="XXXXX").add_to(m)
        st_folium(m, width='100%', height=200, returned_objects=[])

    with col2:
        st.markdown('### Status')

        sub_col1, sub_col2 = col2.columns((1,1))
        with sub_col1:
            st.metric("Status", overall_status,"")
        with sub_col2:  
            st.metric("Overall Progress", overall_progress,"")

        hr()

        st.markdown('### Statistics')
        st.metric("Remaining Days", remaining_days, "")
        st.info("Coming Soon")
        
    hr()








    # Row B
    st.markdown('### Work Progress Chart')

 




   

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

    newdf = newdf.merge(df_project, on="Project ID", how="left")

    # st.write(newdf)





    start_date_proj = pd.to_datetime(df['Start']).min().date()

    end_date_proj = pd.to_datetime(df['End']).max().date()



    

    newdf['Today'] = date_today

    newdf['Start Project Date'] = pd.to_datetime(start_date_proj)

    newdf['End Project Date'] = pd.to_datetime(end_date_proj)

    newdf['Last Update'] = pd.to_datetime(newdf['Last Update'])

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


    
    newdf['BOQ List'] = newdf['BOQ Code'].astype(str) + "." + newdf['BOQ Item ID'].astype(str) + " " + newdf['Item'].astype(str)



    label_colors = {
        'condition': [
            {'test' : 'datum.label == "AAA"', 'value': 'steelblue'},
            {'test' : 'datum.label == "BBB"', 'value': 'purple'}],
        'value': 'red'}






    chart = alt.Chart(newdf).mark_bar(cornerRadius=3).encode(
        x=alt.X('Start Date',
                axis = alt.Axis(grid=True, title="", labelOverlap=True, labelAngle=0, orient="bottom",
                                gridOpacity=0.85,
                                offset=-10,
           
                                ),
                scale = alt.Scale(domain=domains)
                ),
        x2='End Date',
        y=alt.Y('BOQ List',
                axis = alt.Axis(grid=True, labelAlign="left", labelLimit=150, labelPadding=150, title=""),
                ),
        tooltip=['Title', 'Item'],
        color=alt.Color('Progress_', scale=alt.Scale(range=range_), legend=None),
    )

    percent_boq = alt.Chart(newdf).mark_text(align='left', baseline='middle', dx=5, color="white", fontWeight="normal").encode(
        y=alt.Y('BOQ List'),
        x=alt.X('Start Date'),
        text='Progress',
        tooltip=['Title', 'Item'],
    )

    start_date_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='right', baseline='middle', color="grey", dx=-2, fontWeight="normal", fontSize=13).encode(
        x = alt.X('Start Date:T'),
        y = 'BOQ List',
        text = 'Start Date',
        tooltip = ['Start Date']
    )

    end_date_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='left', baseline='middle', color="grey", dx=2, fontWeight="normal", fontSize=13).encode(
        x = alt.X('End Date:T'),
        y = 'BOQ List',
        text = 'End Date',
        tooltip = ['End Date']
    )

    status_text = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(align='left', baseline='middle', dx=0, color="black",  fontWeight="normal", fontSize=15).encode(
        y=alt.Y('BOQ List'),
        x=alt.X('end_date_domain'),
        text='Status',
        tooltip=['BOQ ID', 'Title', 'Item', 'Status'],
    )



    #! Today Part
    today_date_line = alt.Chart(newdf).mark_rule(color="red").encode(
        x = 'Today',
        tooltip=['Today'],
        size=alt.value(0.5),
    )

    today_date_label = alt.Chart(newdf).mark_text(
        align='center', baseline='bottom', color="red", fontWeight="normal", fontSize=14
    ).encode(
        x=alt.X('Today:T'),
        y = alt.value(0),
        text = 'Today'
    )

    today_date_tag = alt.Chart(newdf).mark_text(
        align='center', baseline='bottom', color="red", fontWeight="normal", fontSize=14, dy=-15, text="Today"
    ).encode(
        x=alt.X('Today:T'),
        y = alt.value(0),
    )



    #! Start Project Date Part
    start_date_line = alt.Chart(newdf).mark_rule(color='blue').encode(
        x = 'Start Project Date',
        size=alt.value(0.1),
    )
    start_date_label = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='center', baseline='bottom', color="blue",  fontWeight="normal", fontSize=14).encode(
        x = alt.X('Start Project Date:T'),
        y = alt.value(0),
        text = 'Start Project Date'
    )
    start_date_tag = alt.Chart(newdf).mark_text(
        align='center', baseline='bottom', color="blue", fontWeight="normal", fontSize=14, dy=-15, text="Start Project Date"
    ).encode(
        x=alt.X('Start Project Date:T'),
        y = alt.value(0),
    )



    #! End Project Date Part
    end_date_line = alt.Chart(newdf).mark_rule(color='blue').encode(
        x = 'End Project Date',
        size=alt.value(0.1),
    )
    end_date_label = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='center', baseline='bottom', color="blue",  fontWeight="normal", fontSize=14).encode(
        x = alt.X('End Project Date:T'),
        y = alt.value(0),
        text = 'End Project Date'
    )
    end_date_tag = alt.Chart(newdf).mark_text(
        align='center', baseline='bottom', color="blue", fontWeight="normal", fontSize=14, dy=-15, text="End Project Date"
    ).encode(
        x=alt.X('End Project Date:T'),
        y = alt.value(0),
    )



    #! Last Update Project Date Part
    update_date_line = alt.Chart(newdf).mark_rule(color='orange').encode(
        x = 'Last Update',
        size=alt.value(0.1),
    )
    update_date_label = alt.Chart(newdf[newdf["Status"].notnull()]).mark_text(
        align='center', baseline='bottom', color="orange",  fontWeight="normal", fontSize=14).encode(
        x = alt.X('Last Update:T'),
        y = alt.value(0),
        text = 'Last Update'
    )
    update_date_tag = alt.Chart(newdf).mark_text(
        align='center', baseline='bottom', color="orange", fontWeight="normal", fontSize=14, dy=-15, text="Last Update"
    ).encode(
        x=alt.X('Last Update:T'),
        y = alt.value(0),
    )
    







    chart_all = alt.layer(
                          start_date_text, end_date_text, 
                          
                          start_date_line, start_date_label, start_date_tag,
                          end_date_line, end_date_label, end_date_tag,

                          chart, percent_boq, 

                          update_date_line, update_date_label, update_date_tag,

                          today_date_line, today_date_label, today_date_tag,
                          status_text)


    st.altair_chart(chart_all, use_container_width=True)



    hr()

    st.markdown("### BOQ List")
    df_report = df[['BOQ ID', 'Title', 'Item', 'Unit', 'Target Quantity', 'Actual Quantity']]
    df_report['Diff Quantity'] = df['Target Quantity'] - df['Actual Quantity']
    st.dataframe(df_report)





if (not project_selected in list(df['Project ID'])) and (project_selected != "P0"):
    st.warning("Data Not Found")