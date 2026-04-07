import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

df = pd.read_csv('/home/abir/PaPa/MyGym/DataPractice/Phy1/raw_data/atmosphere_nasa_clean.csv')

def rho_base(h, rho_0 = 1.225, H= 8500):
    h = np.asarray(h)
    return rho_0 * np.exp(-h/H)
residual = df['density_kg_m3'] - rho_base(df['altitudes_m'])
df['residual_kg_m3'] = residual
residual_func = CubicSpline(df['altitudes_m'], df['residual_kg_m3'], bc_type= 'not-a-knot')

def rho_hybrid(h):
    h = np.asarray(h)
    correction = residual_func(h)
    return rho_base(h) + correction

g = 9.81
m = 2.0
Vo = float(input("Input initial velocity:" ))
theta_deg = float(input("Input initial angle:" ))
theta_rad = np.radians(theta_deg)
Cd = 0.5
A = 0.15
Vxo = Vo* np.cos(theta_rad)
Vyo = Vo* np.sin(theta_rad)
state = np.array([0.0, 0.0, Vxo, Vyo])

def derivatives(t,u):
    x, y, Vx, Vy = u
    V = np.sqrt(Vx**2 + Vy**2)
    rho = rho_hybrid(y)
    k_drag = (rho* Cd* A)/(2* m)
    ax = -k_drag * V * Vx
    ay = -g -k_drag * V * Vy
    return np.array([Vx, Vy, ax, ay])

def RK4(u, t, h):
    K1 = derivatives(t, u)
    K2 = derivatives(t+ h/2, u+ h/2*K1)
    K3 = derivatives(t+ h/2, u+ h/2*K2)
    K4 = derivatives(t+h, u+h*K3)
    return u+ h/6*(K1+ 2*K2 + 2*K3 + K4)
dt = 0.01
t = 0.0
trajectory = [state.copy()]
prev_state = state.copy()

while state[1] >= 0:
    prev_state = state.copy()
    state = RK4(state, t, dt)
    t+= dt
    trajectory.append(state.copy())

y1 = prev_state[1]
y2 = state[1]
x1 = prev_state[0]
x2 = state[0]

if abs(y2-y1) > 1e-6:
    Range = x1+ (0-y1)*(x2-x1)/(y2-y1)
else:
    Range = x2

trajectory = np.array(trajectory)
x_max = np.max(trajectory[:, 0])
y_max = np.max(trajectory[:, 1])
plt.plot(trajectory[:, 0], trajectory[:, 1])
plt.axhline(0, color= 'blue', linewidth= 1)
plt.xlabel("Horizontal Distance Travelled (m)")
plt.ylabel("Height (m)")
plt.title(f"Projectile motion (V= {Vo} | Theta= {theta_rad} rad)")

if x_max > 0 and y_max > 0:
    plt.text(x_max * 0.05, y_max * 0.9, f"Mass  = {m} kg", bbox=dict(facecolor='gray', alpha=0.4))
    plt.text(x_max * 0.05, y_max * 0.8, f"Drag Coefficient (Cd) = {Cd}", bbox=dict(facecolor='gray', alpha=0.4))
    plt.text(x_max * 0.05, y_max * 0.7, f"Cross-sectional area of m (A) = {A} m²", bbox=dict(facecolor='gray', alpha=0.4))
    plt.text(x_max * 0.05, y_max * 0.6, f"Range of m (A) = {Range} m", bbox=dict(facecolor='gray', alpha=0.4))
    plt.text(x_max * 0.05, y_max * 0.5, f"Time of flight of m (A) = {t} s", bbox=dict(facecolor='gray', alpha=0.4))

plt.grid()
plt.savefig(f'plot_hybrid.png')
plt.show()








