import pandas as pd
file_input= "us_atmosphere_NASA.csv"
file_output= "atmosphere_nasa_clean.csv"
df = pd.read_csv(file_input, skiprows=4, sep= r'\s+', header= None)
#     r = raw string
#     \s = any whitespace character (space, tab, newline)
#     + = one or more of them
df.columns = ['altitudes_m','density_kg_m3','viscosity_Pa_s']
df['altitudes_m'] = df['altitudes_m']*1000
df = df.astype(float)
df.to_csv(file_output, index= False)

