import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("atmosphere_nasa_clean.csv")
plt.plot(df['altitudes_km'], df['density_kg_m3'])
plt.xlabel('Height(m)')
plt.ylabel('Atmospheric Density(kg/m3)')
plt.title('Atmospheric Density as a Function of Height')
plt.grid(True)
plt.savefig('density_height.png')
plt.show()
