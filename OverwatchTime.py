import datetime
import csv
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import random
import logging


###
# resource_path
#
# param: relative_path - the path of the terminal is
# return: returns the path of the programData folder and where the 
#         OverwatchTimeData must be located.
###
def resource_path(relative_path):
    return os.path.join(os.getenv('ProgramData'), 'OverwatchTimeData', relative_path)


# This is the path for where the logs should be
LOG_FILE_PATH = os.path.join(os.getenv('ProgramData'), 'OverwatchTimeData', 'MainProgram.log')
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

root = tk.Tk()

#Define the start time as a global variable so we can 
# access it whenever we need.
start_time = None 

# Path variables
TIME_LOG_PATH = resource_path('csvs/time_log.csv')
CLOCK_IN_STATUS_PATH = resource_path('csvs/clock_in_status.csv')
IMAGE_DIR = resource_path('images')

###
# read_sessions
#
# return: the csv returned in list form.
###
def read_sessions():
    if not os.path.exists(TIME_LOG_PATH):
        return []
    with open(TIME_LOG_PATH, 'r') as file:
        reader = csv.reader(file)
        sessions = list(reader)
    return sessions

###
# gui_clock_in 
#
# This is a clock in function that operates when the clock in function is
# called. This just makes a msg box that tells you to clock in or out.
###
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

###
# gui_clock_out
# 
# This is a function that saves the session, makes a msg box notifying the user
# that they are clocking out, and sets the program state to clocked out.
###
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


###
# clock_in
#
# This clocks the user in to the primary function. It does this by writing
# true into the "clocked in or not" csv
###
def clock_in():
    try:
        with open(CLOCK_IN_STATUS_PATH, 'w') as file:
            # Remove what was previously written, write True
            file.write('True')
    except FileNotFoundError:
        # If the file doesn't exist, create it and write True
        with open(CLOCK_IN_STATUS_PATH, 'w') as file:
            file.write('True')
    return datetime.datetime.now()

###
# clock_out
#
# param: start_time - this is the time when the session started.
# return: duration - how long the program was running based on start - end.
###
def clock_out(start_time):
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    return duration

###
# check_clocked_in
#
# return: true or false, based on whether or not the person is clocked in
###
def check_clocked_in():
    try:
        with open(CLOCK_IN_STATUS_PATH, 'r') as file:
            status = file.readline().strip()
            return status == 'True'
    except FileNotFoundError:
        return False

###
# save_session
#
# param: duration - how long the user has been logged in for currently
###
def save_session(duration):
    with open(TIME_LOG_PATH, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.date.today(), duration.total_seconds()])

###
# weekly_summary
#
# param: year - what the current year is
# param: week_number - what week it is in the year
###
def weekly_summary(year, week_number):
    sessions = read_sessions()
    weekly_total = sum(float(duration) for date, duration in sessions if datetime.datetime.strptime(date, '%Y-%m-%d').isocalendar()[:2] == (year, week_number))
    return weekly_total

###
# update_weekly_summary
#
# calculates how long the user has been clocked in for
###
def update_weekly_summary():
    current_year, current_week, _ = datetime.datetime.now().isocalendar()
    if os.path.exists(TIME_LOG_PATH):
        total_seconds = weekly_summary(current_year, current_week)
        formatted_time = format_duration(total_seconds)
        summary_label.config(text=f"Total time put in this week: {formatted_time}")
    else:
        summary_label.config(text="No data available for this week.")

###
# on_closing
#
# if the user is currently clocked in, then ensure csv reflects that
###
def on_closing():
    if check_clocked_in():
        with open(CLOCK_IN_STATUS_PATH, 'w') as file:
            file.write('True\n')
            file.write(str(datetime.datetime.now()))
    root.destroy()

###
# format_duration
# 
# This grabs the time in the CSV and converts it to a time format that humans
# like, i.e. 0 days X hours, Y mins, Z seconds
#
# param: seconds - how long in seconds the CSV reflects
###
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

###
# initialize_app
#
# this is necessary processes that need to be done before the program is able
# to run. In this instance, we need to check and see if the user is clocked in 
# or not.
###
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

def check_for_update():
    pass

###
# display_random_image
#
# this picks a random image out of the images folder and sets it as the lock
# screen for that day
###
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

root.mainloop()
