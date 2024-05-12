import datetime
import csv
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import random
import logging
import subprocess


def resource_path(relative_path):
    return os.path.join(os.getenv('ProgramData'), 'OverwatchTimeData', relative_path)


LOG_FILE_PATH = os.path.join(os.getenv('ProgramData'), 'OverwatchTimeData', 'MainProgram.log')
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

root = tk.Tk()

#Define the start time as a global variable so we can 
# access it whenever we need.
start_time = None 

# Path variables
TIME_LOG_PATH = resource_path('csvs/time_log.csv')
TIME_LOG_FOLDER = resource_path('csvs')
CLOCK_IN_STATUS_FOLDER = resource_path('csvs')
CLOCK_IN_STATUS_PATH = resource_path('csvs/clock_in_status.csv')
IMAGE_DIR = resource_path('images')

# Create the csv file if it doesn't exist
def read_sessions():
    if not os.path.exists(TIME_LOG_PATH):
        return []
    with open(TIME_LOG_PATH, 'r') as file:
        reader = csv.reader(file)
        sessions = list(reader)
    return sessions

# GUI
def gui_clock_in():
    if check_clocked_in():
        logging.error("User tried to clock in while already clocked in.")
        messagebox.showerror("Error", "You are already clocked in, please clock out before trying to clock in again.")
    else:
        global start_time
        start_time = clock_in()
        messagebox.showinfo("Clock In", f"Clocked in at {start_time}")
        clock_in_button.config(state="disabled")
        clock_out_button.config(state="normal")


def gui_clock_out():
    if not check_clocked_in():
        messagebox.showerror("Error", "You must clock in first!")
    else:
        global start_time
        end_time = clock_out(start_time)
        save_session(end_time)
        with open(CLOCK_IN_STATUS_PATH, 'w') as file:
            file.write('False')
        messagebox.showinfo("Clock Out", f"Clocked out at {end_time}")
        update_weekly_summary()
        clock_in_button.config(state="normal")
        clock_out_button.config(state="disabled")


def clock_in():
    # See if the CSV's folder exists, if not, create it
    if not os.path.exists(TIME_LOG_FOLDER):
        os.makedirs(TIME_LOG_FOLDER)
    try:
        with open(CLOCK_IN_STATUS_PATH, 'w') as file:
            # Remove what was previously written, write True
            file.write('True')
    except FileNotFoundError:
        # If the file doesn't exist, create it and write True
        with open(CLOCK_IN_STATUS_PATH, 'w') as file:
            file.write('True')
    return datetime.datetime.now()

def clock_out(start_time):
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    return duration

def check_clocked_in():
    # Check if the folder exists, if not, create it
    if not os.path.exists(CLOCK_IN_STATUS_FOLDER):
        os.makedirs(CLOCK_IN_STATUS_FOLDER)
    try:
        with open(CLOCK_IN_STATUS_PATH, 'r') as file:
            status = file.readline().strip()
            return status == 'True'
    except FileNotFoundError:
        return False


def save_session(duration):
    with open(TIME_LOG_PATH, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.date.today(), duration.total_seconds()])


def weekly_summary(year, week_number):
    sessions = read_sessions()
    weekly_total = sum(float(duration) for date, duration in sessions if datetime.datetime.strptime(date, '%Y-%m-%d').isocalendar()[:2] == (year, week_number))
    return weekly_total

def update_weekly_summary():
    current_year, current_week, _ = datetime.datetime.now().isocalendar()
    if os.path.exists(TIME_LOG_PATH):
        total_seconds = weekly_summary(current_year, current_week)
        formatted_time = format_duration(total_seconds)
        summary_label.config(text=f"Total time put in this week: {formatted_time}")
    else:
        summary_label.config(text="No data available for this week.")

def on_closing():
    if check_clocked_in():
        with open(CLOCK_IN_STATUS_PATH, 'w') as file:
            file.write('True\n')
            file.write(str(datetime.datetime.now()))
    root.destroy()

def format_duration(seconds):
    # Convert total seconds into respective time units
    days, seconds = divmod(seconds, 86400)  # 86400 seconds in a day
    hours, seconds = divmod(seconds, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(seconds, 60)  # 60 seconds in a minute

    # Build the duration string conditionally
    duration_parts = []
    if days > 0:
        duration_parts.append(f"{int(days)} days")
    if hours > 0:
        duration_parts.append(f"{int(hours)} hours")
    if minutes > 0:
        duration_parts.append(f"{int(minutes)} mins")
    if seconds > 0 or not duration_parts:
        duration_parts.append(f"{int(seconds)} seconds")

    return ", ".join(duration_parts)

def initialize_app():
    global start_time
    if check_clocked_in():
        with open(CLOCK_IN_STATUS_PATH, 'r') as file:
            lines = file.readlines()
            if len(lines) > 1:
                start_time = datetime.datetime.strptime(lines[1].strip(), "%Y-%m-%d %H:%M:%S.%f")
        clock_in_button.config(state="disabled")  # Optionally disable the Clock In button
        messagebox.showinfo("Welcome Back", "You were clocked in. Please clock out when done.")
    # Check for update

def check_and_update():
    # if the user doesn't want to update, then just continue with the program.
    check_version_script = resource_path('checkVersion.ps1')
    installer_script = resource_path('installer.ps1')
# Run the version check script
    try:
        # Execute the PowerShell script

        result = subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Unrestricted', check_version_script],
                            capture_output=True, text=True)
        # Convert output to boolean (PowerShell outputs True or False as strings)
        versions_match = result.stdout.strip().lower() == 'true'

        # Determine if an update is needed
        update_needed = not versions_match

    except Exception as e:
        logging.error("Failed to check version: " + str(e))
        update_needed = False  # Assuming no update if there's a failure to check

    # Prompt for update if needed
    if update_needed:
        user_response = messagebox.askyesno("Update Available", "An update is available for OverwatchTime. Do you want to update now?")
        if user_response:
            try:
                # Run the installer script
                subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Unrestricted', installer_script])
            except Exception as e:
                logging.error("Update installation failed: " + str(e))
        else:
            logging.info("User chose not to update.")

    # Check for an old executable and remove it
    try:
        old_exe_path = "./OverwatchTime_old.exe"
        if os.path.exists(old_exe_path):
            os.remove(old_exe_path)
            logging.info("Removed old executable.")
        else:
            logging.info("No old executable found.")
        
    except Exception as e:
        logging.error("Failed to remove old executable: " + str(e))


def display_random_image():
    #image_dir = resource_path("images")
    png_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.png')]
    random_png = random.choice(png_files)
    image_path = os.path.join(IMAGE_DIR, random_png)
    image = Image.open(image_path)
    image = image.resize((100, 100), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=photo)
    label.image = photo  # Keep a reference to the image to prevent it from being garbage collected
    label.pack(pady=10)

display_random_image()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.title("Overwatch Time Script")

root.iconbitmap(IMAGE_DIR + '/download.ico')


# Create the buttons
clock_in_button = tk.Button(root, text="Clock In", command=gui_clock_in, height=2, width=15)
clock_in_button.pack(pady=10)

clock_out_button = tk.Button(root, text="Clock Out", command=gui_clock_out, height=2, width=15)
clock_out_button.pack(pady=10)

# Set window size
window_width = 500
window_height = 300

# get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# calculate position x and y coordinates, center of screen
x = (screen_width/2) - (window_width/2)
y = (screen_height/2) - (window_height/2)

# set geometry to center of screen
root.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

summary_label = tk.Label(root, text="Total seconds tracked this week: 0")
summary_label.pack(pady=20)

# Start the app
initialize_app()

update_weekly_summary()

check_and_update()

root.mainloop()

# Check for a new version of the program
