import serial
import time
import json


SERIAL_PORT = "COM3" 
BAUD_RATE = 115200
DATA_FILE = "asset_data.json"
ASSET_ID = "Wheelchair_01" # The ID for the dashboard

asset_database = {}

print(f"Connecting to serial port {SERIAL_PORT}...")
print("If this fails, check your port in Arduino IDE.")
print("!! IMPORTANT: Close the Arduino Serial Monitor first! !!")

try:
    # Open the serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Wait for the connection to establish
    
    print("Connection successful. Reading data...")

    while True:
        # Read one line of data from the ESP
        try:
            line = ser.readline().decode('utf-8').strip()
            
            # Your ESP prints: "1699824147000,RSSI:-55,DIST_m:1.234"
            # Or: "1699824147000,NOT_FOUND"
            
            if line and "RSSI:" in line:
                # Find the RSSI part
                parts = line.split(',')
                rssi_str = ""
                for part in parts:
                    if "RSSI:" in part:
                        rssi_str = part
                        break
                
                # Extract the number
                rssi_val = int(rssi_str.split(':')[1])
                
                # Update our database dictionary
                asset_database[ASSET_ID] = {
                    "rssi": rssi_val,
                    "last_seen": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Write the new data to the JSON file
                with open(DATA_FILE, 'w') as f:
                    json.dump(asset_database, f, indent=4)
                    
                print(f"Updated {ASSET_ID} -> RSSI: {rssi_val}")

            elif "NOT_FOUND" in line:
                print("Asset not found in scan...")
                # You could choose to update the JSON with an "Unknown" status here
            
        except UnicodeDecodeError:
            print("Serial data error. Skipping line.")
        except KeyboardInterrupt:
            print("Stopping script...")
            break
            
except serial.SerialException as e:
    print(f"\n--- ERROR ---")
    print(f"Failed to connect to {SERIAL_PORT}. Reason: {e}")
    print("Is the port correct? Is the ESP plugged in?")
    print("Is the Arduino Serial Monitor closed?")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")