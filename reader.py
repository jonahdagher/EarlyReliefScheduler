import streamlit as st
from streamlit_calendar import *
from streamlit_components import *
import os
from csv_classes import *

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

import copy



db_path = "C:\\Users\\jonah\\Desktop\\Waterfall\\database.db"
schedule_files = os.listdir("C:\\Users\\jonah\\Desktop\\Waterfall\\schedules")

schedule_path = st.selectbox("Select Schedule Path", 
             options=schedule_files)

schedule = Schedule("C:\\Users\\jonah\\Desktop\\Waterfall\\schedules\\" + schedule_path)
selected_year_month = str(st.date_input("Input Schedule Month"))[:7]
if st.button("UPDATE"):
    schedule.year_month = selected_year_month

try:
    people = schedule.getProviderSchedules()

    with st.expander("Colors"):
        for color in schedule.all_colors["rgb"]:
            st.color_picker(f"#{color}", f"#{color}")

    with st.expander("People"):
        provider_rows = schedule.getProviderRows()
        for item in provider_rows:
            st.write(item["name"].split(",")[0])

    engine = create_engine("sqlite:///database.db", echo=False)

    Base = declarative_base()
    class Provider(Base):
        __tablename__ = "providers"

        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False, unique=True)
        time = Column(String)

        dates = relationship("ProviderDate", back_populates="provider")

    class ProviderDate(Base):
        __tablename__ = "provider_dates"

        id = Column(Integer, primary_key=True)
        provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
        date = Column(String, nullable=False)

        status = Column(String)

        color = Column(String)
        value = Column(String)

        provider = relationship("Provider", back_populates="dates")

        __table_args__ = (UniqueConstraint("provider_id", "date", name="uq_provider_date"),)

    class PreviousRankings(Base):
        __tablename__ = "previous_rankings"

        id = Column(Integer, primary_key = True)
        year_month = Column(String, nullable=False, unique=True)
        ranking_lists = Column(JSON)

    def remove_provider_dates_by_month(session, year_month):
        month_prefix = f"{year_month}-"
        session.execute(
            delete(ProviderDate
                ).where(ProviderDate.date.like(f"{month_prefix}%"))
        )



    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    remove_provider_dates_by_month(session, schedule.year_month)

    VALID_TIMES = get_group("settings.json", "VALID_TIMES")
    provider_schedules = schedule.getProviderSchedules()

    detected_values = set()

    for provider in provider_schedules:
        sched = provider_schedules[provider]
        for entry in sched.schedule:
            if entry.value != None and "-" in str(entry.value):
                detected_values.add(entry.value)

    VALID_TIMES += list(detected_values)


    for provider_name, days in schedule.getProviderSchedules().items():

        provider_times = []
        most_common_time = None
        max_occurances = 0 

        for day in days:
            if str(day.value) in VALID_TIMES:
                provider_times.append(str(day.value))

        for time in VALID_TIMES:
            if provider_times.count(time) > max_occurances:
                max_occurances = provider_times.count(time)
                most_common_time = time

        provider = session.execute(select(Provider).where(Provider.name == provider_name)).scalar_one_or_none()

        if provider is None:
            provider = Provider(name=provider_name, time=most_common_time)
            session.add(provider)
            session.flush()

        provider_dates = []
        for d in days:

            exit_time = str(d.value) if str(d.value) in VALID_TIMES else "OFF"

            provider_dates.append(
                ProviderDate(
                    provider = provider,
                    date = d.date,
                    color = d.color,
                    value = exit_time
                )
            )



        session.add_all(provider_dates)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()

    CORAL_SPRINGS = get_group("providerAttributes.json", "coralsprings")

    def get_provider_names_working_time_on_day(session, day: str, time_value: str):
        return session.execute(
            select(Provider.name)
            .join(ProviderDate)
            .where(ProviderDate.date == day, 
                ProviderDate.value == time_value,
                ProviderDate.color != "#92D050", 
                Provider.name.notin_(CORAL_SPRINGS)),
            ).scalars().all()

    def get_provider_names_working_time(session, time_value: str):
        return session.execute(
            select(Provider)
            .where(Provider.time == time_value,
                Provider.name.notin_(CORAL_SPRINGS),)
            ).scalars().all()

    last_month_rankings = session.scalar(
        select(PreviousRankings
            ).where(PreviousRankings.year_month == previous_year_month(schedule.year_month))
            )


    if last_month_rankings != None:
        ranking_730 = last_month_rankings.ranking_lists["730"]
        ranking_530 = last_month_rankings.ranking_lists["530"]
    else:
        ranking_730 = [p.name for p in get_provider_names_working_time(session, "730")]
        ranking_530 = [p.name for p in get_provider_names_working_time(session, "530")]

    per_diem = set(get_group("providerAttributes.json", "perdiem"))

    all_days = [s.date for s in schedule.getProviderSchedules()["DAGHER, MANSOUR"]]

    time_dict = {
        "730": {

        },
        "530": {

        },
        "330": {

        },
        "930": {

        },
    }

    for day in all_days:
        working_730 = set(get_provider_names_working_time_on_day(session, day, "730"))

        # perdiem_working = [n for n in ranking_730 if n in working_730 and n in per_diem]
        nonper_working  = [n for n in ranking_730 if n in working_730 and n not in per_diem]

        ranked_list = nonper_working

        if not nonper_working:
            continue

        top = nonper_working[0]
        ranking_730.remove(top)
        ranking_730.append(top)

        time_dict["730"][day] = ranked_list

    for day in all_days:
        working_530 = set(get_provider_names_working_time_on_day(session, day, "530"))

        extra_working = session.execute(select(Provider.name).join(ProviderDate).where(ProviderDate.color == "#92D050", ProviderDate.date == day)).scalars().all()
        extra_working = [name + " (EX)" for name in extra_working]

        perdiem_working = [n + " (PRN)" for n in ranking_530 if n in working_530 and n in per_diem]
        nonper_working  = [n for n in ranking_530 if n in working_530 and n not in per_diem and n not in extra_working]

        ranked_list = extra_working + perdiem_working + nonper_working


        if not nonper_working:
            continue

        top = nonper_working[0]
        ranking_530.remove(top)
        ranking_530.append(top)

        # st.write(day, ranked_list)  # debug
        time_dict["530"][day] = ranked_list

    for day in all_days:
        working_330 = get_provider_names_working_time_on_day(session, day, "330")
        time_dict["330"][day] = working_330

    for day in all_days:
        working_930 = get_provider_names_working_time_on_day(session, day, "930")
        time_dict["930"][day] = working_930

    current_month_saved = session.scalar(select(PreviousRankings
                            ).where(PreviousRankings.year_month == schedule.year_month))

    if current_month_saved:
        current_month_saved.ranking_lists = {
            "730" : ranking_730,
            "530" : ranking_530
        }

    else:
        month_rankings = PreviousRankings(
        year_month = schedule.year_month,
        ranking_lists = {
            "730" : ranking_730,
            "530" : ranking_530
        }
        )
        session.add(month_rankings)


    try:
        session.commit()
    except IntegrityError:
        session.rollback()

    import pandas as pd

    df = pd.DataFrame(index=range(200), columns=range(17))

    row = 0
    row_number = 0
    chunk_width = 3
    max_length = 0

    for i, day in enumerate(all_days):
        list_530 = time_dict["530"].get(day, [])
        list_330 = time_dict["330"].get(day, [])
        list_730 = time_dict["730"].get(day, [])
        list_930 = time_dict["930"].get(day, [])
        j = (i*chunk_width) - (15*row_number)

        header_330 = ["[3:30]"] if len(list_330) > 0 else []
        header_930 = ["[9:30]"] if len(list_930) > 0 else []

        regular_valid_times = get_group("settings.json", "VALID_TIMES") + ["OFF"]

        special_shifts = session.execute(
            select(Provider.name,
                   ProviderDate.value
                   ).join(ProviderDate
                          ).where(ProviderDate.value.not_in(regular_valid_times), ProviderDate.date == day)
                          ).all()
        
        special_shifts = [shift[0] + f" ({shift[1]})" for shift in special_shifts]
        
        
        header_special = ["[Other Shifts]"] if special_shifts else []
        

        list_530_330 = [day, ""] + ["[5:30]"] + list_530 + [""] + header_330 + list(list_330)
        list_730_930 = ["", ""] + ["[7:30]"] + list_730 + [""] + header_930 + list(list_930) + header_special + special_shifts

        max_length = max(len(list_530_330), len(list_730_930), max_length)

        for k, name in enumerate(list_530_330):
            k = k + row
            df.iloc[k, j] = name

        for k, name in enumerate(list_730_930):
            k = k + row
            df.iloc[k, j+1] = name

        if (i+1) % 5 == 0 and i != 0:
            row_number += 1
            row += max_length + 1
            max_length = 0

    st.dataframe(df)

except TypeError:
    st.warning("Please select a valid date")