import csv
import requests
import numpy as np
import pandas as pd
import datetime


class KyudenAreaScraper:

    def _parseCsvs(self):
        # Main Page
        # https://www.kyuden.co.jp/td_service_wheeling_rule-document_disclosure

        # CSVs change format halfway thru
        # https://www.kyuden.co.jp/var/rev0/0254/3833/area_jyukyu_jisseki_H28_1Q.csv
        #  to
        # https://www.kyuden.co.jp/var/rev0/0254/3845/area_jyukyu_jisseki_2019_1Q.csv
        #  then final one is first month in set?
        # https://www.kyuden.co.jp/var/rev0/0254/3850/area_jyukyu_jisseki_2020_07.csv

        CSV_URLS = []

        groupNum = "0257"  # Changes every month
        fileNumStart = 4370  # Changes every month
        # TODO: Move to a HTML parsing version to get the new endpoints each month

        for year in range(28, 31):
            for quarter in range(1, 5):
                url = "https://www.kyuden.co.jp/var/rev0/{groupNum}/{fileNum}/area_jyukyu_jisseki_H{year}_{quarter}Q.csv".format(
                    fileNum=fileNumStart + len(CSV_URLS),
                    year=year,
                    quarter=quarter,
                    groupNum=groupNum
                )
                CSV_URLS.append(url)

        for year in range(2019, 2021):
            for quarter in range(1, 5):
                url = "https://www.kyuden.co.jp/var/rev0/{groupNum}/{fileNum}/area_jyukyu_jisseki_{year}_{quarter}Q.csv".format(
                    fileNum=fileNumStart + len(CSV_URLS),
                    year=year,
                    quarter=quarter,
                    groupNum=groupNum
                )
                CSV_URLS.append(url)

        # TODO - See how it changes next month
        CSV_URLS.append(
            "https://www.kyuden.co.jp/var/rev0/0257/4387/area_jyukyu_jisseki_2020_07_08.csv",
        )

        dtypes = {
            "MWh_area_demand": int,
            "MWh_nuclear": int,
            "MWh_fossil": int,
            "MWh_hydro": int,
            "MWh_geothermal": int,
            "MWh_biomass": int,
            "MWh_solar_output": int,
            "MWh_solar_throttling": int,
            "MWh_wind_output": int,
            "MWh_wind_throttling": int,
            "MWh_pumped_storage": int,
            "MWh_interconnectors": int,
        }

        headersList = [
            "datetime",
            "MWh_area_demand",
            "MWh_nuclear",
            "MWh_fossil",
            "MWh_hydro",
            "MWh_geothermal",
            "MWh_biomass",
            "MWh_solar_output",
            "MWh_solar_throttling",
            "MWh_wind_output",
            "MWh_wind_throttling",
            "MWh_pumped_storage",
            "MWh_interconnectors",
        ]

        # DATE_TIME
        # エリア需要〔MWh〕
        # 原子力〔MWh〕
        # 火力〔MWh〕
        # 水力〔MWh〕
        # 地熱〔MWh〕
        # バイオマス〔MWh〕
        # 実績〔MWh〕
        # 抑制量〔MWh〕
        # 実績〔MWh〕
        # 抑制量〔MWh〕
        # 揚水〔MWh〕
        # 連系線〔MWh〕

        converters = {
            "MWh_area_demand": lambda x: (x.replace(',', '')),
            "MWh_nuclear": lambda x: (x.replace(',', '')),
            "MWh_fossil": lambda x: (x.replace(',', '')),
            "MWh_hydro": lambda x: (x.replace(',', '')),
            "MWh_geothermal": lambda x: (x.replace(',', '')),
            "MWh_biomass": lambda x: (x.replace(',', '')),
            "MWh_solar_output": lambda x: (x.replace(',', '')),
            "MWh_solar_throttling": lambda x: (x.replace(',', '')),
            "MWh_wind_output": lambda x: (x.replace(',', '')),
            "MWh_wind_throttling": lambda x: (x.replace(',', '')),
            "MWh_pumped_storage": lambda x: (x.replace(',', '')),
            "MWh_interconnectors": lambda x: (x.replace(',', '')),
        }

        def _getCSV(url):
            print("  -- getting:", url)
            try:
                data = pd.read_csv(
                    url,
                    skiprows=2,
                    encoding="cp932",
                    header=None,
                    parse_dates=[0],
                    names=headersList,
                    usecols=range(len(headersList)),
                    converters=converters
                )
            except Exception as e:
                print("Caught error \"{error}\" at {url}".format(
                    error=e, url=url))
                return None

            data = data.dropna()
            return data

        print("Reading CSVs")

        dataList = map(_getCSV, CSV_URLS)

        df = pd.concat(dataList)
        df = df.reset_index(drop=True)

        # Set Dtypes
        df = df.apply(
            lambda x: pd.to_numeric(x, errors='coerce', downcast="integer") if x.name != "datetime" else x)
        # Convert Throttling to INT (for now TODO: move everything to float)
        df['MWh_solar_throttling'] = df['MWh_solar_throttling'].apply(
            lambda x: int(x))
        df['MWh_wind_throttling'] = df['MWh_wind_throttling'].apply(
            lambda x: int(x))

        print(df.info)
        print(df.dtypes)

        return df

    def get_json(self):
        df = self._parseCsvs()
        return df.to_json(orient='index', date_format="iso")

    def convert_df_to_json(self, df):
        df.reset_index(inplace=True)
        return df.to_json(orient='index', date_format="iso")

    def get_csv(self):
        df = self._parseCsvs()
        return df.to_csv(index=False)

    def convert_df_to_csv(self, df):
        return df.to_csv(index=False)

    def get_dataframe(self):
        return self._parseCsvs()
