from myobd import OBD
import tkinter as tk


def check_temp():
    global obd_connection
    try:
        if obd_connection is None:
            obd_connection = OBD()
        temperature = obd_connection.get_coolant_temp()
        output.insert(tk.END, f"Coolant Temperature: {temperature}\n")
    except Exception as e:
        output.insert(tk.END, f"{e}\n")


def run_scan():
    global obd_connection
    output.delete("1.0", tk.END)
    try:
        if obd_connection is None:
            obd_connection = OBD()
        dtcs = obd_connection.get_dtc()
        output.insert(tk.END, f"DTCs: {dtcs}\n")
    except Exception as e:
        output.insert(tk.END, f"{e}\n")


def start_live_updates():
    global live_updating, obd_connection
    live_updating = True
    if obd_connection is None:
        try:
            obd_connection = OBD()
            sensor_labels["Connection"].config(text="Connection Successful")
        except Exception as e:
            sensor_labels["Connection"].config(text=f"{e}")
            obd_connection = None
            return
    update_sensors()


def stop_live_updates():
    global live_updating
    live_updating = False


def update_sensors():
    global obd_connection

    if not live_updating:
        return

    if obd_connection is None:
        root.after(1000, update_sensors)
        return

    try:
        rpm = obd_connection.get_rpm()
        speed = obd_connection.get_speed()
        coolant_temp = obd_connection.get_coolant_temp()
        fuel_pressure = obd_connection.get_fuel_pressure()
        fuel_system_status = obd_connection.fuel_system_status()
        maf = obd_connection.get_maf_airflow_rate()

        o2_values = {}
        for i in range(1, 9):
            try:
                o2_values[i] = obd_connection.get_oxygen(i)
            except Exception:
                o2_values[i] = None

        if coolant_temp is not None:
            sensor_labels["Coolant Temp."].config(
                text=f"Coolant Temp.: {coolant_temp}",
                fg="red" if coolant_temp >= 100 else "green",
            )
        else:
            sensor_labels["Coolant Temp."].config(text="Coolant Temp.: --", fg="black")

        sensor_labels["RPM"].config(text=f"RPM: {rpm if rpm is not None else '--'}")
        sensor_labels["Speed"].config(text=f"Speed: {speed if speed is not None else '--'}")
        sensor_labels["Fuel System Status"].config(
            text=f"Fuel System Status: {fuel_system_status if fuel_system_status is not None else '--'}"
        )
        sensor_labels["Fuel Pressure"].config(
            text=f"Fuel Pressure: {fuel_pressure if fuel_pressure is not None else '--'}"
        )
        sensor_labels["MAF"].config(text=f"MAF Airflow Rate: {maf if maf is not None else '--'}")

        for i in range(1, 9):
            key = f"O2_{i}"
            val = o2_values.get(i)
            sensor_labels[key].config(text=f"O2 Sensor {i}: {val if val is not None else '--'}")

        sensor_labels["Connection"].config(text="Connection Successful")

    except Exception as e:
        sensor_labels["Connection"].config(text=f"{e}")

    root.after(1000, update_sensors)


def show_main_menu():
    stop_live_updates()
    sensor_menu.pack_forget()
    output.pack(expand=True, fill="both", padx=10, pady=10)
    main_menu.pack(pady=10, before=output)


def show_sensor_menu():
    main_menu.pack_forget()
    output.pack_forget()
    sensor_menu.pack()
    start_live_updates()


root = tk.Tk()
root.title("OBD-II Scanner")
root.geometry("600x400")

live_updating = False
obd_connection = None

main_menu = tk.Frame(root)

run_button = tk.Button(main_menu, text="Scan for Codes", command=run_scan)
run_button.pack(side="left", padx=10)

sensor_button = tk.Button(main_menu, text="Sensor Data", command=show_sensor_menu)
sensor_button.pack(side="left", padx=10)

main_menu.pack(pady=10)

sensor_menu = tk.Frame(root)

sensor_labels = {
    "Connection": tk.Label(sensor_menu, text="Not connected", font=("Arial", 12)),
    "RPM": tk.Label(sensor_menu, text="RPM: --", font=("Arial", 12)),
    "Speed": tk.Label(sensor_menu, text="Speed: --", font=("Arial", 12)),
    "Coolant Temp.": tk.Label(sensor_menu, text="Coolant Temp.: --", font=("Arial", 12)),
    "Fuel System Status": tk.Label(sensor_menu, text="Fuel System Status: --", font=("Arial", 12)),
    "Fuel Pressure": tk.Label(sensor_menu, text="Fuel Pressure: --", font=("Arial", 12)),
    "MAF": tk.Label(sensor_menu, text="MAF Airflow Rate: --", font=("Arial", 12)),
}

for lbl in sensor_labels.values():
    lbl.pack(pady=5, anchor="w")

for i in range(1, 9):
    key = f"O2_{i}"
    sensor_labels[key] = tk.Label(sensor_menu, text=f"O2 Sensor {i}: --", font=("Arial", 12))
    sensor_labels[key].pack(pady=2, anchor="w")

back_button = tk.Button(sensor_menu, text="Back", command=show_main_menu)
back_button.pack(side="left", padx=10)

output = tk.Text(root, wrap=tk.WORD)
output.pack(expand=True, fill="both", padx=10, pady=10)

root.mainloop()