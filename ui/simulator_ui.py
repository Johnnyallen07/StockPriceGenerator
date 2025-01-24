import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from models.gbm import generate_gbm_prices
from models.svm import generate_svm_prices
from ui.interval_ui import ModelInterval
from ui.util import parse_float


# -----------------------------------------
# Main Application Class
# -----------------------------------------
class StockSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Interval Stock Simulator")
        self.root.geometry("800x960")

        # List to hold ModelInterval objects
        self.model_intervals = []

        self._create_ui()

        self.simulation_results = {}

    def _create_ui(self):
        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Add Interval", command=lambda: ModelInterval.add_interval(self)).pack(side="left",
                                                                                                          padx=5)
        ttk.Button(btn_frame, text="Run Simulation", command=self.run_simulation).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_simulation).pack(side="left",
                                                                                         padx=5)  # New Export Button

        # Frame for intervals
        self.interval_container = ttk.LabelFrame(self.root, text="Intervals")
        self.interval_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Start with a single interval by default
        ModelInterval.add_interval(self)

    # Inside StockSimulatorGUI class

    def run_simulation(self):
        """
        Gathers configurations from all intervals, runs the appropriate simulation
        for each interval (GBM or SVM), concatenates the resulting price paths, and
        plots them in a new subwindow.
        """
        interval_configs = []
        # 1) Collect and validate intervals
        for idx, interval_obj in enumerate(self.model_intervals, start=1):
            cfg = interval_obj.get_configuration()

            try:
                start_day = int(cfg["start"])
                end_day = int(cfg["end"])
                if start_day >= end_day:
                    raise ValueError(f"Interval {idx}: Start day must be < End day.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return

            interval_configs.append(cfg)

        # 2) Sort intervals by start day
        interval_configs.sort(key=lambda c: int(c["start"]))

        # 3) Initialize lists to collect overall OHLC data
        overall_days = []
        overall_open = []
        overall_close = []
        overall_high = []
        overall_low = []

        last_price = None
        current_offset = 0

        for i, icfg in enumerate(interval_configs, start=1):
            model = icfg["model"]
            params = icfg["params"]

            try:
                start_day = int(icfg["start"])
                end_day = int(icfg["end"])
                T = end_day - start_day  # Number of days in interval

                if T <= 0:
                    messagebox.showerror("Interval Error", f"Interval {i} has invalid length.")
                    return

                # Common parameters
                dt = parse_float(params.get("Time Step (dt)", "1/365"))

                if model == "Geometric Brownian Motion (GBM)":
                    S0 = last_price if last_price is not None else float(params.get("Initial Stock Price (S0)", "100"))
                    mu = parse_float(params.get("Drift (mu)", "0.15"))
                    sigma = parse_float(params.get("Volatility (sigma)", "0.05"))

                    days, open_p, close_p, high_p, low_p = generate_gbm_prices(
                        T, dt, S0, mu, sigma
                    )

                elif model == "Stochastic Volatility Model (Heston)":
                    S0 = last_price if last_price is not None else float(params.get("Initial Stock Price (S0)", "100"))
                    v0 = parse_float(params.get("Initial Variance (v0)", "0.04"))
                    kappa = parse_float(params.get("Mean Reversion Speed (kappa)", "3.0"))
                    theta = parse_float(params.get("Long-term Mean Var (theta)", "0.04"))
                    sigma_v = parse_float(params.get("Vol of Vol (sigma)", "0.6"))
                    rho = parse_float(params.get("Correlation (rho)", "-0.7"))
                    mu = parse_float(params.get("Base Drift (mu)", "0.05"))

                    # Bubble/Crash parameters
                    bubble_start = int(params.get("Bubble Start", "0"))
                    bubble_end = int(params.get("Bubble End", "0"))
                    bubble_mu_extra = parse_float(params.get("Bubble Extra Drift (Δmu)",
                                                             "0.15")) if "Bubble Extra Drift (Δmu)" in params else None
                    crash_day = int(
                        params.get("Crash Day", bubble_end))  # Assuming crash_day is day number within the interval
                    crash_factor = parse_float(params.get("Crash Factor", "0.70")) if "Crash Factor" in params else None


                    days, open_p, close_p, high_p, low_p = generate_svm_prices(
                        T, dt, S0, v0, kappa, theta, sigma_v, rho, mu,
                        bubble_start=bubble_start,
                        bubble_end=bubble_end,
                        bubble_mu_extra=bubble_mu_extra,
                        crash_day=crash_day,
                        crash_factor=crash_factor
                    )

                else:
                    messagebox.showerror("Model Error", f"Interval {i}: Unknown model '{model}'")
                    return

            except ValueError as e:
                messagebox.showerror("Parameter Error", f"Interval {i}: {e}")
                return

            # Adjust days to global timeline
            days = days + current_offset
            current_offset += T

            # Append to overall lists
            overall_days.extend(days)
            overall_open.extend(open_p)
            overall_close.extend(close_p)
            overall_high.extend(high_p)
            overall_low.extend(low_p)

            # Update last_price for next interval
            last_price = close_p[-1]


        self.simulation_results = {
            "Day": np.array(overall_days),
            "Open": np.array(overall_open),
            "Close": np.array(overall_close),
            "High": np.array(overall_high),
            "Low": np.array(overall_low)
        }

        self._plot_result(overall_days, overall_close)

    def _plot_result(self, days, prices):
        """
        Create a new Toplevel window and plot the final price path.
        """
        plot_window = tk.Toplevel(self.root)
        plot_window.title("Simulation Results")
        plot_window.geometry("800x600")

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(days, prices, label="Simulated Stock Price", color="blue")
        ax.set_title("Combined Intervals Simulation")
        ax.set_xlabel("Day")
        ax.set_ylabel("Price")
        ax.grid(True)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_simulation(self):
        """
        Exports the simulation results to a CSV file with columns:
        Day, Open, Close, High, Low
        """
        if not self.simulation_results:
            messagebox.showerror("Export Error", "No simulation data to export. Please run the simulation first.")
            return

        # Prompt user to select save location
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title="Save Simulation Results")
        if not file_path:
            return  # User cancelled the save dialog

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Day", "Open", "Close", "High", "Low"])  # Header

                for day, open_p, close_p, high_p, low_p in zip(
                        self.simulation_results["Day"],
                        self.simulation_results["Open"],
                        self.simulation_results["Close"],
                        self.simulation_results["High"],
                        self.simulation_results["Low"]):
                    writer.writerow([day, open_p, close_p, high_p, low_p])

            messagebox.showinfo("Export Successful", f"Simulation results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting: {e}")




