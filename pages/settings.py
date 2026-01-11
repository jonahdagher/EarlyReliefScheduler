import streamlit as st
import json
from streamlit_components import *
from csv_classes import *
import os

schedule_files = os.listdir("C:\\Users\\jonah\\Desktop\\Waterfall\\schedules")

schedule_path = st.selectbox("Select Schedule Path", 
             options=schedule_files)
schedule = Schedule("C:\\Users\\jonah\\Desktop\\Waterfall\\schedules\\" + schedule_path)

schedule.year_month = "2026-01"

people = schedule.getProviderSchedules()
st.subheader("PERDIEM")
group_editor("providerAttributes.json", list(people.keys()), "perdiem")
st.subheader("CORAL SPRINGS")
group_editor("providerAttributes.json", list(people.keys()), "coralsprings")
