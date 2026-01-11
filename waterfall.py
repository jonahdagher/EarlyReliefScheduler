import streamlit as st
from streamlit_calendar import *
import pandas as pd
import copy
import random

# from streamlitV9 import *

group_530 = [
    "LALANI",
    "SOLTIS",
    "MUNCASTER",
    "RUPIN",
    "CEVALLOS",
    "DIAZ",
    "MARTIN",
    "DELVECCHIO",
    "LYEW-AYEE",
    "SCHULTZ",
    "RIPPY",
    "KATZ K.",
    "VALENTINE",
    "HOPFINGER",
    "NAZAIRE",
    "HAYWORTH",
]

group_730 = [
    "WILLIAMS A.",
    "LEBLANC",
    "DAGHER",
    "KATZ B.",
    "SAIDI-JOHNSON",
    "GOORDEEN C.",
    "WILLIAMS E.",
    "VAZQUEZ",
    "PRATHER",
    "SHAPIRO J.",
    "SHAPIRO P.",
    "SCHMIDT",
    "BABYAK",
    "PINLAC",
    "HAMADE",
    "MCDONALD",
]

group_ignore = [
    "BOZ",
    "GABRIC",
    "AUGUSTIN",
    "RAWLINGS",
    "MILBERY",
    "ARAFA",
    "MILLS",
    "MAZZA",
    "NAGANOOLIL",
    "MAZA",
    "MORAES",
    "CODRINGTON",
    "ABRAMSON",
    "SHEPPLE",
    "CAMERON",
    "AKHAVAN",
    "SOOKNANAN",
    "SHAIRO J.",
    "SWIMM",
    "DASTRUP"
]

all_days = [day for day in get_all_days() if day >= "2025-12-27"]

ranking_730 = copy.deepcopy(group_730)
ranking_530 = copy.deepcopy(group_530)

ranking_dict = dict()

for day in all_days:

    ranking_dict[day] = {
        "7:30": [],
        "5:30": [],
        "ignore": [],
        "error": []
    }

    persons_for_day = get_persons_for_day("days_scheduled", day)
    for person in persons_for_day:
        if person in group_730:
            person_time = "7:30"
        elif person in group_530:
            person_time = "5:30"
        elif person in group_ignore:
            person_time = "ignore"
        else:
            person_time = "error"

        ranking_dict[day][person_time].append(person)



for day in all_days:
    day_ranked = []
    for person in group_730:
        if person in ranking_dict[day]["7:30"]:
            day_ranked.append(person)

    top_person = day_ranked[0]
    top_person_index = group_730.index(top_person)

    group_730.pop(top_person_index)
    group_730.append(top_person)

    ranking_dict[day]["7:30"] = day_ranked

for day in all_days:
    day_ranked = []
    for person in group_530:
        if person in ranking_dict[day]["5:30"]:
            day_ranked.append(person)

    top_person = day_ranked[0]
    top_person_index = group_530.index(top_person)

    group_530.pop(top_person_index)
    group_530.append(top_person)

    ranking_dict[day]["5:30"] = day_ranked





for day in ranking_dict:
    st.header(day)
    st.subheader("7:30")
    st.write(ranking_dict[day]["7:30"])
    st.subheader("5:30")
    st.write(ranking_dict[day]["5:30"])


