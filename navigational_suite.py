import tkinter as tk
from tkinter import ttk

# Import each GUI as a function from your modules
from heading_distance_v0_4 import build_gui as build_heading_distance_gui
from arrival_point_calculator_v0_5 import build_gui as build_arrival_point_gui
from great_circule_v0_3 import build_gui as build_great_circle_gui

root = tk.Tk()
root.iconbitmap("compass256.ico")
root.title("Navigation Suite (WGS84 Calculators)")
root.geometry("615x450")
root.resizable(False, False)

main_container = ttk.Frame(root)
main_container.pack(fill="both", expand=True)

notebook = ttk.Notebook(main_container)
notebook.pack(fill='both', expand=False, padx=5, pady=5)
notebook.configure(height=380)

tab1 = ttk.Frame(notebook, height=355, width=615)
tab2 = ttk.Frame(notebook, height=355, width=615)
tab3 = ttk.Frame(notebook, height=355, width=615)

notebook.add(tab1, text="| Heading & Distance Calculations |")
notebook.add(tab2, text="| Arrival Point Calculations |")
notebook.add(tab3, text="| Great Circle Calculations |")

# Each module is responsible for populating its tab's widgets
build_heading_distance_gui(tab1)
build_arrival_point_gui(tab2)
build_great_circle_gui(tab3)

# Author Footnote
footer = ttk.Label(
    main_container,
    text="Developed by Ricardo Carvalho · Navigation Suite (WGS84) · PAM 2025",
    font=("Arial", 8, "italic")
)
footer.pack(side="bottom", pady=(0, 5))

root.mainloop()
