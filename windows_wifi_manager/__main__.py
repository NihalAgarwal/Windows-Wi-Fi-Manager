""" This script file is the main script file which is the front interface of this app
and also all other functionality of other modules can be accessed by the GUI interface
it creates. This module basically creates the directory where the App content will
be stored and also responsible for the support to every other modules.
"""

import ctypes
import os
import time
import tkinter as tk

import appdirs
import requests

import top_level_window as db
from display_data import WifiDisplayBox
from wifi_connection import SystemWifiConnection

SOFTWARE_NAME = "SavedPasswordFinder"
SOFTWARE_AUTHOR = "NihalAgarwal"
APP_DIR = appdirs.user_data_dir(SOFTWARE_NAME, SOFTWARE_AUTHOR)

if not os.path.isdir(APP_DIR):
    os.makedirs(APP_DIR)


# THE BELOW FUNCTIONS ARE THE FUNCTION WHICH ARE CALLED BY THE WIDGETS
# OR TRIGGERED BY THE WIDGETS

def about():
    """ Describe about the software and what it does and also contact
    details to developer, when user or end user face any issue.
    """
    db.About(main_window)


def update():
    """ Check if software has latest version or not"""
    try:
        time.sleep(4)
        _ = requests.get('http://www.google.com/', timeout=5)
        db.MessageBox(main_window, "Version: 1.0v \n\n No Update Available!", "warning")
    except requests.ConnectionError:
        db.MessageBox(main_window, "Check Your Internet Connection", "error")


def add_profile():
    """ Add new Wi-Fi profile to the system."""

    db.AddProfile(main_window, APP_DIR)


def refresh_treeview():
    """ Refresh the software and search for all saved networks and
    add it to the TreeView. It will display the 'rotating' gif until
    the task done.
    """

    def update_gif_frame(index):
        """ Update the frame at every call."""
        single_frame = GIF_FRAMES[index]
        index += 1
        gif_display_label.configure(image=single_frame)
        # Check that all frames are utilized
        if index >= len(GIF_FRAMES):
            wdb.refresh_treeview()
            gif_display_label.destroy()
            return
        TREE_VIEW_FRAME.after(50, update_gif_frame, index)

    gif_display_label = tk.Label(TREE_VIEW_FRAME)
    gif_display_label.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
    TREE_VIEW_FRAME.after(50, gif_display_label.lift)
    TREE_VIEW_FRAME.after(50, update_gif_frame, 0)


def delete_profile():
    """ Call delete_profile method of WifiDisplayBox to delete a wifi profile."""
    wdb.delete_profile(main_window)


def on_exiting():
    """ End the process and quit the software"""

    result = db.QuitWindow(main_window)
    if result.temp.get():
        for i in os.listdir(APP_DIR):
            if i != 'temp_':
                os.remove(APP_DIR + "\\" + i)
        main_window.destroy()


def find_network():
    """ Check if system is connect to any network. If yes the
    network name is return and button value is modified to 'refresh'
    (if no network connected) otherwise button value is modified to
    'disconnect' and label is updated as network name.
    """
    ssid_name: "Name of system connected Network" = system_wifi_connection.is_connected()

    if ssid_name is not None:
        refresh_disconnect_button.configure(text="Disconnect",
                                            command=disconnect_button)
        current_network_label.configure(text=ssid_name, foreground="green")

    else:
        refresh_disconnect_button.configure(text="Refresh",
                                            command=find_network)
        current_network_label.configure(text="No Network", foreground="red")


def disconnect_button():
    """ Disconnect form the current network. """
    disconnected = system_wifi_connection.disconnect_connection()
    if disconnected:
        refresh_disconnect_button.configure(text="Refresh",
                                            command=find_network)
        current_network_label.configure(text="No Network", foreground="red")
        text = "You had to manually connect to same or different network."
        db.MessageBox(main_window, text, "warning")  # pop-up window


# Creating and configuring Main Window
main_window = tk.Tk()
main_window.configure(background='white', highlightbackground="grey")
main_window.title("Password Finder")
try:
    # the below line of code will avoid blurry looking GUI by increasing DPI.
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    main_window.geometry("900x600")

except Exception:
    main_window.geometry("900x500")

main_window.minsize(800, 350)
main_window.iconbitmap("data\\images\\wifi2.ico")

# Creating MENU and SUBMENU
MENU = tk.Menu(main_window)
SUBMENU = tk.Menu(main_window, tearoff=0)
main_window.config(menu=MENU)
MENU.add_cascade(label="Help", menu=SUBMENU)
SUBMENU.add_command(label="About", command=about)
SUBMENU.add_separator()
SUBMENU.add_command(label="Check for updates", command=update)
SUBMENU.add_separator()
SUBMENU.add_command(label="Quit", command=on_exiting)

# Theme for Buttons
STYLE = tk.ttk.Style()
STYLE.configure('TButton', font=("Playfair Display", 15))
STYLE.map('TButton', font=[('active', ("Playfair Display", 12))],
          background=[('active', 'blue')])

# Getting GIF_FRAME for refresh button when clicked
GIF_FRAMES = [tk.PhotoImage(file="data\\images\\loader.gif", format="gif -index %i" % i)
              for i in range(20)] * 3

# Frame1 for system connected network display
TOP_HORIZONTAL_FRAME = tk.Frame(main_window)
# Frame2 for TreeView
TREE_VIEW_FRAME = tk.Frame(main_window, background='white')
# Frame3 for refresh, delete, add profile.
VERTICAL_BUTTON_FRAME = tk.Frame(main_window, background='white')

# Create object to easily reference its method and fields(e.g., SSID name)
system_wifi_connection: 'instance of SystemWifiConnection' = SystemWifiConnection(main_window)

# Displays the heading(title)
HEADING_LABEL = tk.Label(TOP_HORIZONTAL_FRAME, text="Current Network: ",
                         font=("Playfair Display", 13, "bold"))

# Button for disconnection or refresh
refresh_disconnect_button = tk.ttk.Button(TOP_HORIZONTAL_FRAME, style='TButton')

# Displays network name
current_network_label = tk.Label(TOP_HORIZONTAL_FRAME,
                                 font=("Playfair Display", 13, "bold"))

# packing
HEADING_LABEL.pack(padx=10, pady=10, side=tk.LEFT)
current_network_label.pack(padx=10, pady=10, side=tk.LEFT)
refresh_disconnect_button.pack(padx=10, pady=10, side=tk.LEFT)
find_network()

# Defining and packing buttons for frame2
REFRESH_BUTTON = tk.ttk.Button(VERTICAL_BUTTON_FRAME,
                               text="Refresh List", style='TButton',
                               cursor="hand2", command=refresh_treeview)

DELETE_BUTTON = tk.ttk.Button(VERTICAL_BUTTON_FRAME,
                              text="Delete WiFi", style='TButton',
                              cursor="hand2", command=delete_profile)

ADD_PROFILE_BUTTON = tk.ttk.Button(VERTICAL_BUTTON_FRAME,
                                   text="Add Profile", style='TButton',
                                   cursor="hand2", command=add_profile)

# Creating TreeView and packing it to the frame2
wdb: WifiDisplayBox = WifiDisplayBox(APP_DIR, TREE_VIEW_FRAME)

# Packing all three buttons( refresh, delete, add_profile)
REFRESH_BUTTON.pack(side=tk.TOP, pady=25, padx=10, anchor="center")
DELETE_BUTTON.pack(side=tk.TOP, pady=25, padx=10, anchor="center")
ADD_PROFILE_BUTTON.pack(side=tk.TOP, pady=25, padx=10, anchor="center")

# Packing frame1, frame2 and frame3
TOP_HORIZONTAL_FRAME.pack(side="top", fill=tk.BOTH)
VERTICAL_BUTTON_FRAME.pack(side="right", fill=tk.Y, padx=5, pady=5)
TREE_VIEW_FRAME.pack(side="left", fill=tk.BOTH, padx=5, pady=5, expand=1)

# Hold window until user close it manually
main_window.protocol("WM_DELETE_WINDOW", on_exiting)
main_window.mainloop()
