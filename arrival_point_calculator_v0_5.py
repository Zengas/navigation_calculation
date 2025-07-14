# arrival_point_calculator_v0_5.py

import tkinter as tk
from tkinter import ttk, messagebox
from rhumb_v0_2 import Rhumb
import math

def build_gui(parent):
    # Title Label
    title = ttk.Label(
        parent,
        text="Enter Starting Coordinates, Distance (NM), and Azimuth (°)",
        font=("Arial", 10, "italic")
    )
    title.pack(pady=(10, 2))

    EXPLANATION_MESSAGE = (
        "\nThis function calculates the Arrival Coordinates (rhumb line - constant bearing) given departing coordinates, distance, and azimuth. \n\nIts accuracy for distance starts to decrease beyond 300 nautical miles, as it does not represent the shortest path. For longer distances or critical accuracy, great circle calculations are recommended."
    )

    # === Main Input Frame ===
    main_input_frame = ttk.Frame(parent)
    main_input_frame.pack(pady=5, padx=5)

    # Variables for hemispheres
    dep_lat_hemi = tk.StringVar(value="N")
    dep_lon_hemi = tk.StringVar(value="W")

    # --- Coordinate Section ---
    def coordinate_section(parent, label, lat_hemi_var, lon_hemi_var):
        section = ttk.LabelFrame(parent, text=label, padding=10)
        ttk.Label(section, text="Latitude:").grid(row=0, column=0, sticky="e", pady=2)
        lat_deg = ttk.Entry(section, width=6); lat_deg.grid(row=0, column=1)
        ttk.Label(section, text="°").grid(row=0, column=2)
        lat_min = ttk.Entry(section, width=8); lat_min.grid(row=0, column=3)
        ttk.Label(section, text="'").grid(row=0, column=4)
        ttk.Radiobutton(section, text="N", variable=lat_hemi_var, value="N").grid(row=0, column=5)
        ttk.Radiobutton(section, text="S", variable=lat_hemi_var, value="S").grid(row=0, column=6)

        ttk.Label(section, text="Longitude:").grid(row=1, column=0, sticky="e", pady=2)
        lon_deg = ttk.Entry(section, width=6); lon_deg.grid(row=1, column=1)
        ttk.Label(section, text="°").grid(row=1, column=2)
        lon_min = ttk.Entry(section, width=8); lon_min.grid(row=1, column=3)
        ttk.Label(section, text="'").grid(row=1, column=4)
        ttk.Radiobutton(section, text="W", variable=lon_hemi_var, value="W").grid(row=1, column=5)
        ttk.Radiobutton(section, text="E", variable=lon_hemi_var, value="E").grid(row=1, column=6)
        return section, lat_deg, lat_min, lon_deg, lon_min

    dep_section, dep_lat_deg, dep_lat_min, dep_lon_deg, dep_lon_min = coordinate_section(
        main_input_frame, "Departing Coordinates", dep_lat_hemi, dep_lon_hemi
    )

    # --- Leg Parameters Section ---
    leg_frame = ttk.LabelFrame(main_input_frame, text="Leg Parameters", padding=10)
    ttk.Label(leg_frame, text="Distance (NM):").grid(row=0, column=0, sticky="e", padx=(0, 4), pady=2)
    dist_entry = ttk.Entry(leg_frame, width=10)
    dist_entry.grid(row=0, column=1, pady=2)

    ttk.Label(leg_frame, text="Azimuth (°):").grid(row=1, column=0, sticky="e", padx=(0, 4), pady=2)
    az_entry = ttk.Entry(leg_frame, width=10)
    az_entry.grid(row=1, column=1, pady=2)

    # --- Layout configuration ---
    main_input_frame.columnconfigure(0, weight=1)
    main_input_frame.columnconfigure(1, weight=0)
    main_input_frame.columnconfigure(2, weight=1)
    dep_section.grid(row=0, column=0, padx=(0, 12), sticky="e")

    sep = ttk.Separator(main_input_frame, orient="vertical")
    sep.grid(row=0, column=1, sticky="ns", padx=2)
    leg_frame.grid(row=0, column=2, padx=(12, 0), sticky="w")

    # --- Buttons Frame ---
    btn_frame = ttk.Frame(parent)
    btn_frame.pack(pady=(5, 0))

    # --- Result Text ---
    result_text = tk.Text(
        parent,
        height=12,
        width=66,
        font=("Courier New", 11),
        wrap="word",
        state="normal"
    )
    result_text.insert(tk.END, EXPLANATION_MESSAGE)
    result_text.config(state="disabled")
    result_text.pack(pady=10)

    # ========== Helper functions ==========

    def validate_inputs(deg_str, min_str, max_deg, label):
        deg = float(deg_str)
        mins = float(min_str)

        if not (0 <= deg <= max_deg):
            raise ValueError(f"{label}: Degrees must be between 0 and {max_deg}.")
        if not (0 <= mins < 60):
            raise ValueError(f"{label}: Minutes must be between 0 and 59,99.")
        if deg == max_deg and mins > 0:
            raise ValueError(f"{label}: When degrees = {max_deg}, minutes must be 0.")

    def ddm_to_decimal(degrees, minutes, hemi):
        degrees = float(degrees)
        minutes = float(minutes)
        value = degrees + minutes / 60
        if hemi in ("S", "W"):
            value = -value
        return value

    def decimal_to_ddm(val, hemi_pos, hemi_neg, deg_digits=2):
        hemi = hemi_pos if val >= 0 else hemi_neg
        abs_val = abs(val)
        degrees = int(abs_val)
        minutes = (abs_val - degrees) * 60
        deg_str = str(degrees).zfill(deg_digits)
        min_str = f"{minutes:05.2f}"
        return f"{deg_str}° {min_str}' {hemi}"

    latest_result = {"lat2": None, "lon2": None, "lat_ddm": None, "lon_ddm": None}

    def calculate():
        try:
            # Validate latitude
            validate_inputs(dep_lat_deg.get(), dep_lat_min.get(), 90, "Latitude")
            # Validate longitude
            validate_inputs(dep_lon_deg.get(), dep_lon_min.get(), 180, "Longitude")
            # Validate azimuth
            azimuth = float(az_entry.get())
            if not (0 <= azimuth < 360):
                raise ValueError("Azimuth must be between 0 and 359.99 degrees.")

            # Validate distance
            distance_nm = float(dist_entry.get())
            if distance_nm < 0:
                raise ValueError("Distance must be non-negative.")

            # Convert coordinates
            lat1 = ddm_to_decimal(dep_lat_deg.get(), dep_lat_min.get(), dep_lat_hemi.get())
            lon1 = ddm_to_decimal(dep_lon_deg.get(), dep_lon_min.get(), dep_lon_hemi.get())

            r = Rhumb()
            res = r.Direct(lat1, lon1, azimuth, distance_nm * 1852.0)
            lat2 = res['lat2']
            lon2 = res['lon2']

            # Format results
            lat_ddm = decimal_to_ddm(lat2, "N", "S", deg_digits=2)
            lon_ddm = decimal_to_ddm(lon2, "E", "W", deg_digits=3)
            result_str = (
                f"\n"
                f"   --- Arrival Point Calculation Result ---\n\n"
                f"   Arrival Latitude : { ' ' + lat_ddm}\n"
                f"   Arrival Longitude: {lon_ddm}"
            )
            result_text.config(state="normal")
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, result_str)
            result_text.config(state="disabled")

            # Store result
            latest_result["lat2"] = lat2
            latest_result["lon2"] = lon2
            latest_result["lat_ddm"] = lat_ddm
            latest_result["lon_ddm"] = lon_ddm

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=parent)

    def clear():
        for e in [dep_lat_deg, dep_lat_min, dep_lon_deg, dep_lon_min, dist_entry, az_entry]:
            e.delete(0, tk.END)
        dep_lat_hemi.set("N")
        dep_lon_hemi.set("W")
        result_text.config(state="normal")
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, EXPLANATION_MESSAGE)
        result_text.config(state="disabled")
        for key in latest_result: latest_result[key] = None

    def show_graph():
        try:
            azimuth = az_entry.get()
            distance = dist_entry.get()
            if not azimuth or not distance:
                messagebox.showinfo("Graph", "Please enter both Azimuth and Distance first.", parent=parent)
                return

            azimuth = float(azimuth)
            distance = float(distance)

            popup = tk.Toplevel(parent)
            popup.title("Arrival Point Graph")
            try:
                popup.iconbitmap("compass256.ico")
            except Exception:
                pass
            popup.geometry("350x410")
            popup.resizable(False, False)

            canvas = tk.Canvas(popup, width=330, height=330, bg="white")
            canvas.pack(pady=10)

            center_x = 165
            center_y = 165
            radius = 120

            canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="black", width=2)
            font_c = ("Arial", 12, "bold")
            canvas.create_text(center_x, center_y - radius - 15, text="N", font=font_c)
            canvas.create_text(center_x + radius + 15, center_y, text="E", font=font_c)
            canvas.create_text(center_x, center_y + radius + 15, text="S", font=font_c)
            canvas.create_text(center_x - radius - 15, center_y, text="W", font=font_c)
            canvas.create_line(center_x, center_y - radius, center_x, center_y + radius, dash=(2, 2))
            canvas.create_line(center_x - radius, center_y, center_x + radius, center_y, dash=(2, 2))

            arrow_len = radius * 0.92
            angle_rad = math.radians(azimuth - 90)
            x_end = center_x + arrow_len * math.cos(angle_rad)
            y_end = center_y + arrow_len * math.sin(angle_rad)
            canvas.create_line(center_x, center_y, x_end, y_end, fill="red", width=4, arrow=tk.LAST)

            msg = f"Azimuth  : {azimuth:.2f}°\nDistance: {distance:.2f} NM"
            label = ttk.Label(popup, text=msg, font=("Arial", 11, "italic"))
            label.pack(pady=(2, 10))
            popup.transient(parent)
        except Exception as e:
            messagebox.showerror("Graph Error", f"Could not display graph:\n{e}", parent=parent)

    ttk.Button(btn_frame, text="Calculate", command=calculate).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Clear", command=clear).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="Graph", command=show_graph).grid(row=0, column=2, padx=10)

# End of build_gui
