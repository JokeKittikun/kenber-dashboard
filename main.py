import pandas as pd
import numpy as np
import streamlit as st

# Google Sheet
from gspread_pandas import Spread,Client
from google.oauth2 import service_account

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Create a Google Authentication Connect Object
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scope = scope)
client = Client(scope = scope, creds = credentials)
spreadsheetname = "Database"
spread = Spread(spreadsheetname, client = client)


# st.title("Dashboard")
# st.write("test")

# st.markdown("# Header 1")
# st.markdown("## Header 2")
# st.markdown("### Header 3")
