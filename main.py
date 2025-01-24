import tkinter as tk

from ui.simulator_ui import StockSimulatorGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = StockSimulatorGUI(root)
    root.mainloop()