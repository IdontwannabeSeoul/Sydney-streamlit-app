# del low_df
# del df

import numpy as np
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

# 데이터 호출
# path = 'C:/Users/walte/PycharmProjects/pythonProject1'
low_df = pd.read_csv('low_df.csv')

# 데이터 정제
def cleaning(df):
    # col_rename
    df.rename(columns={'in_out': 'in_out_kor'}, inplace=True)
    df.rename(columns={'places': 'place_kor'}, inplace=True)

    # add_nan_col
    df['in_out_eng'] = np.nan
    df['place_eng'] = np.nan

    # add_eng_col
    df['in_out_eng'] = np.where(df['in_out_kor'] == '실내', 'Indoor', 'Outdoor')
    df['place_eng'] = np.where(df['place_kor'] == '시티 내', 'City', 'No City')

    # replace
    df = df.replace('-', np.nan)
    df = df.replace('월화 휴무', 'M, T')

    # check
    # df[(df['in_out_kor'] == '실내') & (df['in_out_eng'] == 'Outdoor')]
    # df['in_out_kor'].unique()

    return df

# 좌표 정제
def add_point(df):
    # add_point
    df.loc[df['destinations_eng'] == 'The University of Sydney', 'point'] = '-33.888190349104256, 151.1867379777887'
    df.loc[df['destinations_eng'] == 'Black Star Pastry', 'point'] = '-33.86917730857161, 151.20802044518595'
    df.loc[df['destinations_eng'] == 'White Rabbit Gallery', 'point'] = '-33.88633322413459, 151.20021755155494'
    df.loc[df['destinations_eng'] == 'Opera House', 'point'] = '-33.8566240007045, 151.215253780389'
    df.loc[df['destinations_eng'] == 'Harbour Bridge', 'point'] = '-33.85177443544334, 151.21084239488715'
    df.loc[df['destinations_eng'] == 'Single O', 'point'] = '-33.880901318132906, 151.20974305525263'
    df.loc[df['destinations_eng'] == 'Carriageworks', 'point'] = '-33.89317826936465, 151.19190318039088'
    df.loc[df['destinations_eng'] == 'Hyde Park', 'point'] = '-33.871249556281825, 151.2116023602141'
    df.loc[df['destinations_eng'] == 'Bondi Beach', 'point'] = '-33.8914943942121, 151.27669442594475'
    df.loc[df['destinations_eng'] == 'Taronga Zoo', 'point'] = '-33.84335123195417, 151.2413525245663'
    df.loc[df['destinations_eng'] == 'Hyde Park Barracks', 'point'] = '-33.86938086696323, 151.21260645340317'
    df.loc[df['destinations_eng'] == 'Justice & Police Museum', 'point'] = '-33.862009310815615, 151.21228379573157'
    df.loc[df['destinations_eng'] == 'Blue Mountains', 'point'] = '-33.385214041477596, 150.48914608881867'
    df.loc[df['destinations_eng'] == 'Blackheath', 'point'] = '-33.63564752614859, 150.28475570524606'
    df.loc[df['destinations_eng'] == 'Hartley Historic Site', 'point'] = '-33.545101750526, 150.17522053776983'
    df.loc[df['destinations_eng'] == 'Stockton Beach', 'point'] = '-32.80480434024352, 151.96004428875077'

    # 분리코드
    df[['lat', 'lon']] = df['point'].str.split(',', expand=True)
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)

    return df

df_cleaning = cleaning(low_df)
df_add_point = add_point(df_cleaning)

# check
# tmp = df[df['destinations_eng'] == 'The University of Sydney']
# df_add_point.to_csv(path + '/tmp.csv', index=False)

# 페이지 설정
st.set_page_config(page_title="MAP", layout="wide")
st.title("⭐ 변백현 팬투어⭐ ")

df = df_add_point

# 필터 UI
st.sidebar.header("🔍 필터")

selected_city = st.sidebar.multiselect(
    "렌트여부",
    options=df["rental"].unique(),
    default=df["rental"].unique()
)

selected_in_out = st.sidebar.multiselect(
    "실내외",
    options=df["in_out_kor"].unique(),
    default=df["in_out_kor"].unique()
)


# 필터 적용
filtered_df = df[
    (df["in_out_kor"].isin(selected_in_out)) &
    (df["rental"].isin(selected_city))
]

# 지도 생성
m = folium.Map(location=[filtered_df["lat"].mean(), filtered_df["lon"].mean()], zoom_start=13)

for _, row in filtered_df.iterrows():
    google_maps_url = f"https://www.google.com/maps?q={row['lat']},{row['lon']}"
    popup_html = f'<a href="{google_maps_url}" target="_blank">{row["destinations_eng"]}</a>'

    icon_color = "red" if row["rental"] == "X" else "blue"  # 조건문은 여기서 처리

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup_html,
        tooltip=row["destinations_kor"],
        icon=folium.Icon(color=icon_color, icon='heart', prefix='fa')
    ).add_to(m)

    bounds = [[filtered_df["lat"].min(), filtered_df["lon"].min()],
              [filtered_df["lat"].max(), filtered_df["lon"].max()]]

    m.fit_bounds(bounds)


# 지도 출력
st.subheader("📍 지도")
st_data = st_folium(m, width=700, height=500)

# 표 출력
st.subheader("🧭 목적지")
columns_to_show = ['destinations_kor', 'in_out_kor', 'place_kor', 'hours', 'holiday']
st.dataframe(filtered_df[columns_to_show].reset_index(drop=True))