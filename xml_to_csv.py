import xml.etree.ElementTree as ET
import pandas as pd

# Load XML file
tree = ET.parse(r"C:\Users\Himanshu Bhatt\Desktop\code\ML project\AQI and source predictor\aqi.xml")
root = tree.getroot()

rows = []

for country in root.findall("Country"):
    for state in country.findall("State"):
        for city in state.findall("City"):
            city_name = city.attrib.get("id")

            for station in city.findall("Station"):
                station_name = station.attrib.get("id")
                date = station.attrib.get("lastupdate")

                data = {
                    "City": city_name,
                    "Station": station_name,
                    "Date": date,
                    "PM2.5": None,
                    "PM10": None,
                    "SO2": None,
                    "CO": None,
                    "OZONE": None
                }

                for pollutant in station.findall("Pollutant_Index"):
                    p_name = pollutant.attrib.get("id")
                    avg = pollutant.attrib.get("Avg")

                    data[p_name] = avg

                rows.append(data)
df = pd.DataFrame(rows)
print(df.head())
df.to_csv(
    r"C:\Users\Himanshu Bhatt\Desktop\code\ML project\AQI and source predictor\aqi_clean.csv",
    index=False
)
