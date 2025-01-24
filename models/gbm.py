import numpy as np
import matplotlib.pyplot as plt

def generate_gbm_prices(T, dt, S0, mu, sigma, steps_per_day=4, seed=None):
    """
    Generates a Geometric Brownian Motion price path with OHLC data.

    :param T: Total number of days (integer)
    :param dt: Time step in years per day (e.g. 1/365)
    :param S0: Initial stock price
    :param mu: Drift (annual)
    :param sigma: Volatility (annual)
    :param steps_per_day: Number of intra-day steps to simulate
    :param seed: Optional random seed for reproducibility
    :return: days (np.array), open_prices, close_prices, high_prices, low_prices
    """
    if seed is not None:
        np.random.seed(seed)

    total_steps = T * steps_per_day
    dt_intra = dt / steps_per_day
    S = np.zeros(total_steps + 1)
    S[0] = S0

    open_prices = []
    close_prices = []
    high_prices = []
    low_prices = []

    current_day = 0
    day_prices = []

    for t in range(1, total_steps + 1):
        Z = np.random.normal()
        S[t] = S[t-1] * np.exp((mu - 0.5 * sigma**2) * dt_intra + sigma * np.sqrt(dt_intra) * Z)
        day_prices.append(S[t])

        if t % steps_per_day == 0:
            open_p = S[t - steps_per_day]
            close_p = S[t]
            high_p = np.max(day_prices)
            low_p = np.min(day_prices)

            open_prices.append(open_p)
            close_prices.append(close_p)
            high_prices.append(high_p)
            low_prices.append(low_p)

            day_prices = []

    days = np.arange(1, T + 1)
    return days, np.array(open_prices), np.array(close_prices), np.array(high_prices), np.array(low_prices)