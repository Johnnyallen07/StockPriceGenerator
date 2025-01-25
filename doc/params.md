# Geometric Brownian Motion (GBM)

- **Initial Price Connected to Previous Ending Price**:  
  Indicates whether the initial price of this interval is connected to the previous interval's ending price.  
  **Default**: `True` (not used explicitly here).

- **Time Step (dt)**:  
  The interval for each simulation step. Typically set based on one day.  
  **Formula**: `1 / (End Day - Start Day)`.

- **Initial Stock Price (S₀)**:  
  The stock price at the first day of the interval.

- **Drift (μ)**:  
  Represents the expected growth rate or trend. A larger value indicates a stronger upward trend.

- **Volatility (σ)**:  
  Measures the variability or uncertainty of the stock price. Higher values indicate more fluctuation.

---

# Stochastic Volatility Model (Heston)

- **Initial Price Connected to Previous Ending Price**:  
  Indicates if this interval's initial price depends on the previous interval's ending price.  
  **Default**: `True`.

- **Time Step (dt)**:  
  The interval for simulation steps. Similar to GBM

- **Initial Stock Price (S₀)**:  
  The stock price at the start of the interval.

- **Initial Variance (v₀)**:  
  The starting variance of the volatility.

- **Mean Reversion Speed (κ)**:  
  Speed at which the variance reverts to its long-term average.

- **Long-term Mean Variance (θ)**:  
  The long-term average variance towards which the model reverts.

- **Volatility of Volatility (σᵥ)**:  
  The degree of fluctuation in the variance itself. (Similar to GBM volatility)

- **Correlation (ρ)**:  
  Correlation between the stock price and its volatility.  
  Negative values (e.g., `-0.7`) indicate that an increase in volatility typically results in a price drop.

- **Base Drift (μ)**:  
  The underlying upward trend of the stock price.

- **Bubble Extra Drift (Δμ)**:  
  Additional drift during a "bubble" period where prices grow more rapidly.

- **Bubble Start**:  
  Day when the bubble phase begins.

- **Bubble End**:  
  Day when the bubble phase ends.

- **Crash Day**:  
  The day when a crash event occurs. (Should between bubble start and end)

- **Crash Factor**:  
  Defines the percentage drop in price during a crash. (0.7 means 70% loss in the crash)
