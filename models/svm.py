import numpy as np



def generate_svm_prices(T, dt, S0, v0, kappa, theta, sigma_v, rho, mu,
                        bubble_start=None, bubble_end=None, bubble_mu_extra=None,
                        crash_day=None, crash_factor=None, steps_per_day=4, seed=None):
    """
    Simplified Stochastic Volatility Model (like Heston),
    with optional bubble/crash logic and OHLC data.

    :param T: Total number of days (int)
    :param dt: day fraction in years
    :param S0: initial stock price
    :param v0: initial variance
    :param kappa, theta, sigma_v: Heston parameters
    :param rho: correlation
    :param mu: base drift
    :param bubble_start, bubble_end: define bubble intervals (if any)
    :param bubble_mu_extra: additional drift during bubble
    :param crash_day: day to trigger crash
    :param crash_factor: factor by which price is multiplied at crash day
    :param steps_per_day: Number of intra-day steps to simulate
    :param seed: optional random seed
    :return: days (np.array), open_prices, close_prices, high_prices, low_prices
    """
    if seed is not None:
        np.random.seed(seed)

    total_steps = T * steps_per_day
    dt_intra = dt / steps_per_day
    days = np.arange(T + 1)
    S = np.zeros(total_steps + 1)
    v = np.zeros(total_steps + 1)
    S[0] = S0
    v[0] = v0

    open_prices = []
    close_prices = []
    high_prices = []
    low_prices = []

    day_prices = []
    current_offset = 0  # To track the current day

    # Generate correlated random draws
    eps1 = np.random.normal(0, 1, total_steps)
    eps2 = np.random.normal(0, 1, total_steps)
    Z1 = eps1
    Z2 = rho * eps1 + np.sqrt(1 - rho ** 2) * eps2

    for t in range(total_steps):
        day = t // steps_per_day + 1  # Current day (1-based)
        if (bubble_start is not None and bubble_end is not None
                and bubble_mu_extra is not None
                and bubble_start <= day <= bubble_end):
            drift_today = mu + bubble_mu_extra
        else:
            drift_today = mu

        # Update variance
        v[t + 1] = (v[t]
                    + kappa * (theta - v[t]) * dt_intra
                    + sigma_v * np.sqrt(max(v[t], 0.0) * dt_intra) * Z2[t])

        if v[t + 1] < 0:
            v[t + 1] = 0

        # Update price (log Euler)
        S[t + 1] = S[t] * np.exp((drift_today - 0.5 * v[t]) * dt_intra
                                 + np.sqrt(max(v[t], 0.0) * dt_intra) * Z1[t])

        # Collect intra-day prices
        day_prices.append(S[t + 1])

        # Crash event
        if crash_day is not None and crash_factor is not None:
            if (t + 1) == crash_day * steps_per_day:
                S[t + 1] = S[t + 1] * crash_factor
                day_prices[-1] = S[t + 1]  # Update the last price after crash

        # If end of the day, record OHLC
        if (t + 1) % steps_per_day == 0:
            open_p = S[t + 1 - steps_per_day]
            close_p = S[t + 1]
            high_p = np.max(day_prices)
            low_p = np.min(day_prices)

            open_prices.append(open_p)
            close_prices.append(close_p)
            high_prices.append(high_p)
            low_prices.append(low_p)

            day_prices = []

    days_array = np.arange(1, T + 1)
    return days_array, np.array(open_prices), np.array(close_prices), np.array(high_prices), np.array(low_prices)
