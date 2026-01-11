import json
import streamlit as st

def group_editor(path, options, groupName):
    if "reset_key" not in st.session_state:
        st.session_state.reset_key = 0

    #get data from json file
    with open(path, "r+") as j:
        json_data = json.load(j)
        current_group = json_data.get(groupName, []) 

        #edit data
        active_group = st.multiselect("Edit", 
                                    options, 
                                    current_group, 
                                    key=f"{groupName}-{st.session_state.reset_key}", 
                                    label_visibility="collapsed")

        #if data is changed prompt to save or revert
        if set(current_group) != set(active_group):

            if st.button("CONFIRM"):

                j.seek(0)
                j.truncate()

                json_data[groupName] = active_group
                json.dump(json_data, j)
                st.rerun

            elif st.button("REVERT"):
                st.session_state.reset_key +=1
                st.rerun()


def get_group(path, groupName):
    with open(path, "r") as j:
        json_data = json.load(j)
        return json_data[groupName]
    
