import tkinter as tk
from tkinter import ttk


class Settings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game Settings")

        # Max Force
        tk.Label(self.root, text="Max Force (lbs):").grid(row=0, column=0, padx=10, pady=10)
        self.max_force = tk.IntVar()
        tk.Entry(self.root, textvariable=self.max_force).grid(row=0, column=1, padx=10, pady=10)

        # Force Mode
        tk.Label(self.root, text="Force Mode:").grid(row=1, column=0, padx=10, pady=10)
        self.force_mode = tk.StringVar()
        self.force_mode_dropdown = ttk.Combobox(self.root, textvariable=self.force_mode)
        self.force_mode_dropdown['values'] = ("Linear", "Normalized", "Asymptotic", "Logarithmic")
        self.force_mode_dropdown.grid(row=1, column=1, padx=10, pady=10)
        self.force_mode_dropdown.current(0)

        # Game Mode
        tk.Label(self.root, text="Game Mode:").grid(row=2, column=0, padx=10, pady=10)
        self.game_mode = tk.StringVar()
        self.game_mode_dropdown = ttk.Combobox(self.root, textvariable=self.game_mode)
        self.game_mode_dropdown['values'] = ("Flappy Bird", "Helicopter Game")
        self.game_mode_dropdown.grid(row=2, column=1, padx=10, pady=10)
        self.game_mode_dropdown.current(1)

        # Save Button
        tk.Button(self.root, text="Save", command=self.save_settings).grid(row=3, columnspan=2, pady=20)

        self.settings = None

    def save_settings(self):
        self.settings = {
            "max_force": self.max_force.get(),
            "force_mode": self.force_mode.get(),
            "game_mode": self.game_mode.get()
        }
        self.root.destroy()

    def get_settings(self):
        self.root.mainloop()
        return self.settings


if __name__ == "__main__":
    settings = Settings()
    user_settings = settings.get_settings()
    print(user_settings)
