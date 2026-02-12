import myobd
import time
import tkinter as tk
from tkinter import messagebox
import sys, os 
# sys.path.append(os.path.dirname(__file__))



# def decode_vin(vin: str):
   # url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/{vin}?format=json"
   # r = requests.get(url, timeout=10)
   # r.raise_for_status()
   # res = r.json()["Results"][0]
    #return {
      #  "Make": res.get("Make"),
       # "Model": res.get("Model"),
       # "ModelYear": res.get("ModelYear"),
       # "Manufacturer": res.get("Manufacturer"),
       # "BodyClass": res.get("BodyClass"),
        #"EngineModel": res.get("EngineModel"),
        #"FuelTypePrimary": res.get("FuelTypePrimary"),
       # "TransmissionStyle": res.get("TransmissionStyle"),
   # }


def check_temp() :
    try:
        obd = myobd.OBD()
    except Exception as e:
        output.insert(tk.END, f"{e}\n")
        return
    temperature=obd.get_coolant_temp()
    output.insert(tk.END,f"Coolant Temperature: {temperature}\n")




def run_scan():

    
    output.delete("1.0", tk.END)
    try:
        obd = myobd.OBD()
    except Exception as e:
        output.insert(tk.END, f"{e}\n")
        return

    dtcs = obd.get_dtc()
    

    output.insert(tk.END, f"DTCs: {dtcs}\n")
    


def start_live_updates():


    global live_updating
    live_updating = True
    update_sensors()

def stop_live_updates():
    live_updating = False

def update_sensors():
    if not live_updating:
        return
    try:
        obd = myobd.OBD() 
        rpm = obd.get_rpm() 
        speed = obd.get_speed() 
        coolant_temp = obd.get_coolant_temp() 
        fuel_pressure = obd.get_fuel_pressure()
        fuel_system_status = obd.fuel_system_status()
        
        o2_values = {}
        for i in range(1, 9):
            try:
                val = obd.get_oxygen(i)
                o2_values[i] = val
            except Exception:
                o2_values[i] = None
        if coolant_temp is not None:
            sensor_labels["Coolant Temp."].config(
                text=f"Coolant Temp.:{coolant_temp}",
                fg="red" if coolant_temp >= 100 else "green"
            )
        else:
            sensor_labels["Coolant Temp."].config(text="Coolant Temp.: --", fg= "green")

# add more sensor labels for above sensors
        sensor_labels["RPM"].config(text=f"RPM: {rpm}")

    except Exception as e:
        sensor_labels["Connection"].config(text=f"{e}")

    root.after(1000,update_sensors)










# ---------- GUI ----------- #

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


main_menu = tk.Frame(root)

run_button = tk.Button(main_menu, text="Scan for Codes", command=run_scan)
run_button.pack(side="left", padx=10)

sensor_button = tk.Button(main_menu, text="Sensor Data", command=show_sensor_menu)
sensor_button.pack(side="left", padx=10)




main_menu.pack(pady=10)


sensor_menu = tk.Frame(root)

sensor_labels = {
    "Connection": tk.Label(sensor_menu, text="Connection Successful", font=("Arial",12)),
    "RPM": tk.Label(sensor_menu, text="RPM: --", font=("Arial", 12)),
    "Speed": tk.Label(sensor_menu, text="Speed: --", font=("Arial", 12)),
    "Coolant Temp.": tk.Label(sensor_menu, text="Coolant Temp: --", font=("Arial", 12)),
    "Fuel System Status": tk.Label(sensor_menu, text="Fuel System Status: --", font=("Arial", 12)),
    "Fuel Pressure": tk.Label(sensor_menu, text="Fuel Pressure: --", font=("Arial", 12)),
    "MAF": tk.Label(sensor_menu, text="MAF Airflow Rate: --", font=("Arial", 12))

    
}


for lbl in sensor_labels.values():
    lbl.pack(pady=5, anchor="w")

for i in range(1,9):
    key=f"O2_{i}"
    sensor_labels[key]= tk.Label(sensor_menu, text=f"O2 Sensor {i}: --",font=("Arial",12))
    sensor_labels[key].pack(pady=2, anchor="w")




#coolant_button = tk.Button(sensor_menu, text="Coolant Temp", command=check_temp)
#coolant_button.pack(side="left", padx=10)

back_button = tk.Button(sensor_menu, text="Back", command=show_main_menu)
back_button.pack(side="left", padx=10)

output = tk.Text(root, wrap=tk.WORD)
output.pack(expand=True, fill="both", padx=10, pady=10)


root.mainloop()
