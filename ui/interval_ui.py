import tkinter as tk
from tkinter import ttk


# -----------------------------------------
# ModelInterval Class
# -----------------------------------------
class ModelInterval:
    """
    Represents a single model interval in the simulator.
    Each interval has:
      - Start day
      - End day
      - Model selection
      - Dynamic model configuration (parameters)
    """
    # Define default parameter sets for each model
    MODEL_PARAMS = {
        "Geometric Brownian Motion (GBM)": {
            "Initial Price Connected to Previous Ending Price": "true",
            "Time Step (dt)": "0.01",
            "Initial Stock Price (S0)": "100",
            "Drift (mu)": "0.15",
            "Volatility (sigma)": "0.05",
        },
        "Stochastic Volatility Model (Heston)": {
            "Initial Price Connected to Previous Ending Price": "true",
            "Time Step (dt)": "1/265",
            "Initial Stock Price (S0)": "100",
            "Initial Variance (v0)": "0.04",
            "Mean Reversion Speed (kappa)": "3.0",
            "Long-term Mean Var (theta)": "0.04",
            "Vol of Vol (sigma)": "0.6",
            "Correlation (rho)": "-0.7",
            "Base Drift (mu)": "0.05",
            "Bubble Extra Drift (Δmu)": "0.15",
            "Bubble Start": "100",
            "Bubble End": "150",
            "Crash Day": "140",
            "Crash Factor": "0.70",

        }
    }

    def __init__(self, parent_ui, interval_number):
        """
        Initializes a ModelInterval.

        :param parent_ui: The main simulator GUI instance (StockSimulatorGUI).
        :param interval_number: The sequential index of this interval.
        """
        self.parent_ui = parent_ui  # Reference to main GUI
        self.interval_number = interval_number

        # Store param widgets in a dict
        self.param_entries = {}

        # -------------------------
        # Main Frame for Interval
        # -------------------------
        self.frame = ttk.LabelFrame(parent_ui.interval_container,
                                    text=f"Interval {self.interval_number}",
                                    padding=(10, 10))
        self.frame.pack(fill="x", pady=5)

        # Row 0: Start Day + End Day + Model + Remove Button
        ttk.Label(self.frame, text="Start Day:").grid(row=0, column=0, sticky="w", pady=2)
        self.start_day = ttk.Entry(self.frame, width=10)
        self.start_day.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(self.frame, text="End Day:").grid(row=0, column=2, sticky="w", padx=(15, 0))
        self.end_day = ttk.Entry(self.frame, width=10)
        self.end_day.grid(row=0, column=3, sticky="w", pady=2)

        # Model Selection
        ttk.Label(self.frame, text="Model:").grid(row=0, column=4, sticky="w", padx=(15, 0))
        self.model_var = tk.StringVar(value="Geometric Brownian Motion (GBM)")
        self.model_menu = ttk.OptionMenu(
            self.frame,
            self.model_var,
            self.model_var.get(),
            *self.MODEL_PARAMS.keys(),
            command=self._on_model_change  # callback to update config
        )
        self.model_menu.grid(row=0, column=5, sticky="w")

        # Remove Button
        remove_btn = ttk.Button(self.frame, text="Remove", command=self._remove_interval)
        remove_btn.grid(row=0, column=6, padx=(15, 0))

        # Initialize Start/End defaults
        if self.interval_number == 1:
            self.start_day.insert(0, "1")
            self.end_day.insert(0, "100")
        else:
            # If there's a previous interval, auto set start day as last's end+1
            last_end = self._get_last_interval_end()
            self.start_day.insert(0, str(last_end + 1))
            self.end_day.insert(0, "365")

        # -------------------------
        # Configuration Sub-Frame
        # -------------------------
        self.config_frame = ttk.LabelFrame(self.frame, text="Model Configuration", padding=(10, 10))
        self.config_frame.grid(row=1, column=0, columnspan=7, pady=(10, 0), sticky="we")

        # Populate parameters for default model
        self._create_param_widgets(model_name=self.model_var.get())

    # --- Static Methods for Interval Management ---

    @staticmethod
    def add_interval(parent_ui):
        """
        Creates and returns a new ModelInterval instance for the given parent UI.
        Also appends it to the parent's interval list and relabels intervals.
        """
        interval_number = len(parent_ui.model_intervals) + 1
        interval_obj = ModelInterval(parent_ui, interval_number)
        parent_ui.model_intervals.append(interval_obj)
        ModelInterval._relabel_intervals(parent_ui)
        return interval_obj

    @staticmethod
    def _relabel_intervals(parent_ui):
        """
        Re-labels intervals in the parent's model_intervals list
        as "Interval X" after add/remove.
        """
        for idx, interval_obj in enumerate(parent_ui.model_intervals, start=1):
            interval_obj.interval_number = idx
            interval_obj.frame.config(text=f"Interval {idx}")

    # --- Event Handlers ---

    def _on_model_change(self, selected_model):
        """
        Called when the user changes the model in the dropdown.
        Destroys old param widgets and recreates them based on new model.
        """
        self._create_param_widgets(model_name=selected_model)

    # --- Interval UI Actions ---
    def _remove_interval(self):
        """
        Removes this interval from parent's list and destroys its frame.
        """
        self.parent_ui.model_intervals.remove(self)
        self.frame.destroy()
        ModelInterval._relabel_intervals(self.parent_ui)

    def _get_last_interval_end(self):
        """
        Returns the end day of the last interval, or 0 if none.
        """
        if not self.parent_ui.model_intervals:
            return 0
        last_interval = self.parent_ui.model_intervals[-1]
        try:
            return int(last_interval.end_day.get())
        except ValueError:
            return 0

    # --- Parameter Management ---
    def _create_param_widgets(self, model_name):
        """
        Clears old param widgets and re-creates them for the selected model.
        """
        # Clear old widgets in config_frame
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.param_entries.clear()

        # Retrieve the default parameter dictionary for the chosen model
        defaults = self.MODEL_PARAMS.get(model_name, {})

        # Create label/entry for each param
        for idx, (param_key, default_val) in enumerate(defaults.items()):
            ttk.Label(self.config_frame, text=f"{param_key}:").grid(row=idx, column=0, sticky="w", pady=2)
            ent = ttk.Entry(self.config_frame, width=20)
            ent.insert(0, default_val)
            ent.grid(row=idx, column=1, sticky="w", padx=5, pady=2)
            self.param_entries[param_key] = ent

    # --- External API ---
    def get_configuration(self):
        """
        Returns a dictionary containing start day, end day, model, and param values.
        """
        params = {}
        for p_key, widget in self.param_entries.items():
            params[p_key] = widget.get().strip()

        return {
            "start": self.start_day.get().strip(),
            "end": self.end_day.get().strip(),
            "model": self.model_var.get(),
            "params": params
        }
