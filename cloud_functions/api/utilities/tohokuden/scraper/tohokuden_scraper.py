import csv
import requests
import numpy as np
import pandas as pd
import datetime


def _renameHeader(header):

    translations = {
        "DATE_TIME": "datetime",
        "エリア需要〔MWh〕": "MWh_area_demand",
        "水力〔MWh〕": "MWh_hydro",
        "火力〔MWh〕": "MWh_fossil",
        "原子力〔MWh〕": "MWh_nuclear",
        "太陽光実績〔MWh〕": "MWh_solar_output",
        "太陽光抑制量〔MWh〕": "MWh_solar_throttling",
        "風力実績〔MWh〕": "MWh_wind_output",
        "風力抑制量〔MWh〕": "MWh_wind_throttling",
        "地熱〔MWh〕": "MWh_geothermal",
        "バイオマス〔MWh〕": "MWh_biomass",
        "揚水〔MWh〕": "MWh_pumped_storage",
        "連系線〔MWh〕": "MWh_interconnectors",
    }

    if header in translations:
        return translations[header]
    return header


def _parseTohokudenCsvs():

    CSV_URLS = []

    for year in range(2016, 2021):
        for quarter in range(1, 5):
            url = "https://setsuden.nw.tohoku-epco.co.jp/common/demand/juyo_{year}_tohoku_{quarter}Q.csv".format(
                year=year,
                quarter=quarter
            )
            CSV_URLS.append(url)

    # DATE_TIME,
    # エリア需要〔MWh〕,
    # 水力〔MWh〕,
    # 火力〔MWh〕,
    # 原子力〔MWh〕,
    # 太陽光実績〔MWh〕,
    # 太陽光抑制量〔MWh〕,
    # 風力実績〔MWh〕,
    # 風力抑制量〔MWh〕,
    # 地熱〔MWh〕,
    # バイオマス〔MWh〕,
    # 揚水〔MWh〕,
    # 連系線〔MWh〕

    dtypes = {
        "エリア需要〔MWh〕": int,
        "水力〔MWh〕": int,
        "火力〔MWh〕": int,
        "原子力〔MWh〕": int,
        "太陽光実績〔MWh〕": int,
        "太陽光抑制量〔MWh〕": int,
        "風力実績〔MWh〕": int,
        "風力抑制量〔MWh〕": int,
        "地熱〔MWh〕": int,
        "バイオマス〔MWh〕": int,
        "揚水〔MWh〕": int,
        "連系線〔MWh〕": int
    }

    def _getTohokudenCSV(url):
        print("  -- getting:", url)
        try:
            data = pd.read_csv(url, skiprows=0, encoding="cp932", dtype=dtypes)
        except Exception as e:
            print("Caught error \"{error}\" at {url}".format(
                error=e, url=url))
            return None
        return data

    print("Reading CSVs")

    dataList = map(_getTohokudenCSV, CSV_URLS)

    df = pd.concat(dataList)

    # Translate Column Headers
    print("Renaming Columns")
    df = df.rename(columns=lambda x: _renameHeader(x), errors="raise")

    df['datetime'] = pd.to_datetime(df['datetime'], infer_datetime_format=True).dt.tz_localize(
        'Asia/Tokyo')

    return df


def get_tohokuden_as_json():
    df = _parseTohokudenCsvs()
    return df.to_json(orient='index', date_format="iso")


def convert_tohokuden_df_to_json(df):
    df.reset_index(inplace=True)
    return df.to_json(orient='index', date_format="iso")


def get_tohokuden_as_csv():
    df = _parseTohokudenCsvs()
    return df.to_csv(index=False)


def convert_tohokuden_df_to_csv(df):
    return df.to_csv(index=False)


def get_tohokuden_as_dataframe():
    return _parseTohokudenCsvs()