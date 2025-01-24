import numpy as np
import matplotlib.pyplot as plt

# --- 1. Parameters ---
T       = 265           # total days
dt      = 1/265         # in years (assuming 1 day = 1/365 year)
S0      = 100.0         # initial price
v0      = 0.04          # initial variance
mu      = 0.05          # base drift (annual)
bubble_mu_extra = 0.15  # extra drift during bubble
kappa   = 3.0
theta   = 0.04
sigma   = 0.6
rho     = -0.7

bubble_start = 200
bubble_end   = 250       # day index for bubble to end
crash_day    = bubble_end
crash_factor = 0.70      # price will drop to 70% of its value at crash day

# --- 2. Storage for results ---
S = np.zeros(T+1)
v = np.zeros(T+1)
S[0] = S0
v[0] = v0

# Random draws for correlated normals
# We need T random draws for each day: Z1, Z2 correlated
eps1 = np.random.normal(0, 1, T)
eps2 = np.random.normal(0, 1, T)
Z1   = eps1
Z2   = rho * eps1 + np.sqrt(1 - rho**2) * eps2

# --- 3. Simulation loop ---
for t in range(T):
    # 3.1 Decide drift for the day (bubble or base)
    if t < bubble_end:
        # During bubble
        drift_today = mu + bubble_mu_extra
    else:
        # Post-bubble
        drift_today = mu

    # 3.2 Update variance (v_t) using Euler discretization
    v[t+1] = ( v[t]
               + kappa * (theta - v[t]) * dt
               + sigma * np.sqrt(max(v[t], 0.0) * dt) * Z2[t] )

    # 3.3 Ensure variance doesn’t go negative numerically
    if v[t+1] < 0:
        v[t+1] = 0

    # 3.4 Update price (S_t) with log-Euler approach
    #    log-return ~ (drift_today - v[t]/2) dt + sqrt(v[t] dt)*Z1[t]
    S[t+1] = S[t] * np.exp((drift_today - 0.5*v[t]) * dt
                           + np.sqrt(max(v[t], 0.0) * dt) * Z1[t])

    # 3.5 Crash event
    if t+1 == crash_day:
        S[t+1] = S[t+1] * crash_factor  # abrupt drop

# --- 4. Plot the results ---
days = np.arange(T+1)
fig, ax1 = plt.subplots(figsize=(10,6))

color1 = 'tab:blue'
ax1.set_xlabel('Day')
ax1.set_ylabel('Price', color=color1)
ax1.plot(days, S, color=color1, label='Simulated Price')
ax1.tick_params(axis='y', labelcolor=color1)

# ax2 = ax1.twinx()  # for volatility on secondary axis
# color2 = 'tab:red'
# ax2.set_ylabel('Variance', color=color2)
# ax2.plot(days, v, color=color2, label='Variance')
# ax2.tick_params(axis='y', labelcolor=color2)

plt.title('Stochastic Volatility Simulation with Bubble & Crash')
fig.tight_layout()
plt.show()
