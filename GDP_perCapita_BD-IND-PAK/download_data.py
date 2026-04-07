import requests
import pandas as pd

countries = ["BGD", "IND", "PAK"]  
indicator = "NY.GDP.PCAP.CD"       
start_year = 2005
end_year = 2025
output_file = "GDP_per_capita_BD_IND_PAK_2005_2025.csv"

url = f"http://api.worldbank.org/v2/country/{';'.join(countries)}/indicator/{indicator}?date={start_year}:{end_year}&format=json&per_page=1000"

print("Fetching data from World Bank API...")
response = requests.get(url)
data = response.json()

records = []
for entry in data[1]:
    country = entry["country"]["value"]
    year = entry["date"]
    value = entry["value"]
    records.append({"Country": country, "Year": int(year), "GDP_per_capita": value})
df = pd.DataFrame(records)

df = df.sort_values(by=["Country", "Year"])

df.to_csv(output_file, index=False)  
print(f"Data saved to {output_file}")

