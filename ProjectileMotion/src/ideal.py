import numpy as np
import matplotlib.pyplot as plt

g = 9.81
for i in range(0,6):
    m = 2.0+ i
# Vo = float(input("Input initial velocity:" ))
# theta_deg = float(input("Input initial angle:" ))
    Vo = 40+ i*5
    theta_deg = 40 +i*8
    theta_rad = np.radians(theta_deg)
    Cd = 0.5 + i*0.05
    rho = 1.2
    A = 0.15
    k_drag = (rho* Cd* A)/(2* m)
    Vxo = Vo* np.cos(theta_rad)
    Vyo = Vo* np.sin(theta_rad)
    state = np.array([0.0, 0.0, Vxo, Vyo]) 

    def derivatives(t,u):
        x, y, Vx, Vy = u  # numpy array. Elements of array u is unpacked into variables x, y, Vx, Vy. So there it will get Vx, Vy.
        V = np.sqrt(Vx**2 + Vy**2)
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
    trajectory = [state.copy()]  # A list that stores the projectile's state (position and velocity) at each time step.
    prev_state = state.copy()  # If you only used state and updated it directly in the loop, you would lose the last valid state where y >= 0 after the loop ends. When the loop exits, state will be the first state where y < 0 (the projectile is below ground). You would have no record of the last state where y >= 0 (the projectile was still above ground).
    while state[1] >= 0:
        prev_state = state.copy()
        state = RK4(state, t, dt)
        t+= dt
        trajectory.append(state.copy())

# range: prev_state is the last point above ground(y>0) . State is the first point  below ground(y<0)
    y1 = prev_state[1]      # At time t, state = [x1, y1, vx1, vy1] where y1 > 0.
    y2 = state[1]           # At time t + dt, state = [x2, y2, vx2, vy2] where y2 < 0
    x1 = prev_state[0]     
    x2 = state[0]
    if abs(y2-y1) > 1e-6:
        Range = x1+ (0-y1)*(x2-x1)/(y2-y1)
    else:
        Range = x2
# The projectile crosses the ground between two time steps.
# You need to estimate the exact x-coordinate where y = 0.
# This is a linear interpolation between the two points (x1, y1) and (x2, y2) to find the x-coordinate where y = 0.
# The slope (m) of the line connecting (x1, y1) and (x2, y2) is:
# m = (y2 - y1) / (x2 - x1)
# This tells you how much y changes for a unit change in x.
# Δx = Δy / m = (0 - y1) / m = (0 - y1) * (x2 - x1) / (y2 - y1)
   # print(f"Range of flight: {Range:.2f} m")
   # print(f"Time of flight: {t:.2f} s")

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
    plt.savefig(f'plot{2+i}.png')
    plt.show()






