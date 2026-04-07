import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

df = pd.read_csv('atmosphere_nasa_clean.csv')
def rho_base(h, rho_0 = 1.225, H= 8500):
    h = np.asarray(h)
    return rho_0 * np.exp(-h/H)
residual = df['density_kg_m3'] - rho_base(df['altitudes_m'])
# print(residual)
df['residual_kg_m3'] = residual
residual_func = CubicSpline(df['altitudes_m'], df['residual_kg_m3'], bc_type= 'not-a-knot')  # CubicSpline is a class constructor that builds an interpolation object.
# CubicSpline(x_data, y_data); residual_func created with it can be called with any number of altitude values. 
def rho_hybrid(h):  
    h = np.asarray(h)
    correction = residual_func(h)
    return rho_base(h) + correction  # Calls globally defined rho_base(h)
df['density_hybrid_kg_m3'] = rho_hybrid(df['altitudes_m'])
df.to_csv('with_hybrid_density.csv')

plt.plot(df['altitudes_m'], df['density_kg_m3'], label='data_density' )
plt.plot(df['altitudes_m'], df['density_hybrid_kg_m3'], label= 'hybrid_density', alpha = 0.4)
plt.legend()
plt.xlabel('Altitude(m)')
plt.ylabel('Density(kg/m3)')
plt.grid(True,alpha= 0.3)
plt.savefig('hybrid_density.png')
plt.show()

