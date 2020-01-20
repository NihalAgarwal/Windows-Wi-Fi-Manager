""" This module is responsible to create Tree View where save wifi in the
system of user will displayed with other data like (SSID name, Authentication,
Key) and also having functionality to delete the Wi-Fi profile from the system
and refresh the content of the TreeView."""

import os
import subprocess
import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as ttk

from . import top_level_window as db
from . import wifi_data as saved_wifi_info


class WifiDisplayBox:
    """ Creates a TreeView and display all the saved wifi and their
    SSID's, Authentication and Password.
    """

    def __init__(self, app_path, frame):
        self.frame = frame
        self.tree_view = None
        self.list_of_children = None
        self.app_path = app_path
        self.getting_data_obj = GettingData(app_path)
        self.create_treeview()
        self.build_tree()
        self.index_of_previous_item = ("", "", False)

    def get_wifi_list(self):
        """ Called generating_wifi_list() function of SavedInfoFile."""
        return self.getting_data_obj.wifi_list()

    def create_treeview(self):
        """ Create tree view and configure style for it."""

        # Defining styling for TreeView.
        style = ttk.Style(self.frame)
        style.configure("Treeview.Heading", font=("Playfair Display", 11,
                                                  'bold'), foreground='#6C7A89')
        style.configure("Treeview", font=('Calibri', 11))
        style.map("Treeview.Heading",
                  font=[('pressed', ("Playfair Display", 9, 'bold'))],
                  foreground=[('pressed', '#264348'), ('active', '#264348')])

        self.tree_view = ttk.Treeview(self.frame, columns=self.getting_data_obj.get_headings(),
                                      show="headings")
        headings_treeview = self.getting_data_obj.get_headings()

        # Defining Headings to the TreeView and defining column width.
        for i in enumerate(headings_treeview):
            self.tree_view.heading(i[0], text=i[1], anchor=tk.NW)
            self.tree_view.column(i[0], width=tkfont.Font().measure(i[1].title()),
                                  minwidth=130, anchor=tk.NW)

        # Adding and Scrollbars to the TreeView.
        vertical_scrollbar = ttk.Scrollbar(orient="vertical", command=self.tree_view.yview)
        horizontal_scrollbar = ttk.Scrollbar(orient="horizontal", command=self.tree_view.xview)
        self.tree_view.configure(yscrollcommand=vertical_scrollbar.set)
        self.tree_view.configure(xscrollcommand=horizontal_scrollbar.set)
        self.tree_view.grid(column=0, row=0, sticky='nsew', in_=self.frame)
        vertical_scrollbar.grid(column=1, row=0, sticky='ns', in_=self.frame)
        horizontal_scrollbar.grid(column=0, row=1, sticky='ew', in_=self.frame)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

    def build_tree(self):
        """ Adding the list of wifi to the treeview in the form of ["name", "", "" ,""]."""

        # Add rows to the TreeView with the column[0] = name
        for item in self.get_wifi_list():
            self.tree_view.insert('', 'end', values=item, tags='ttk')

        # binding the functions
        self.tree_view.tag_bind('ttk', sequence="<<TreeviewSelect>>", callback=self.treeview_select)
        self.list_of_children = list(self.tree_view.get_children())

    def treeview_select(self, _=None):
        """ Function is called when user select any of the row in TreeView and displays
        the SSID, Authentication, Key of the selected row and deletes the SSID,
        Authentication and Key of previous selected row.
        """

        # get id of the selected row.
        item_id = self.tree_view.focus()

        # If user move from previous selected row to newly selected row, it removes
        # the SSId, Authentication, Key of previously selected row(except name).
        if self.index_of_previous_item[-1]:
            values_ = [self.index_of_previous_item[1], "", "", ""]
            self.tree_view.item(self.index_of_previous_item[0], values=values_)

        # The below code displays the SSID, Authentication, Key of newly selected row
        name = self.tree_view.item(item_id)['values'][0]
        current_item_detail = self.getting_data_obj.detailed_list(name)
        self.tree_view.item(item_id, values=[*current_item_detail])
        self.index_of_previous_item = (item_id, name, True)

    def refresh_treeview(self):
        """ Refresh the treeView and add or remove the profile from the TreeView
        if it is not present any more or newly added respectively.
        """

        # If in a TreeView any row is selected then deselect it.
        if self.tree_view.focus():
            self.tree_view.item(self.index_of_previous_item[0],
                                values=[self.index_of_previous_item[-2], "", "", ""])

        if os.path.isfile(self.app_path + "\\Saved Wifi list.txt"):
            os.remove(self.app_path + "\\Saved Wifi list.txt")

        # Generating fresh newly wifi list.
        self.getting_data_obj.create_wifi_list()

        # Modify rows of tree view and remove or add newly added data.

        try:
            self.build_tree()
        except Exception:
            pass

    def delete_profile(self, parent_window):
        """ Delete Wi-Fi profile and all its content from the System."""

        try:
            if len(self.list_of_children) < 1:
                text = "No item available to delete."
                db.MessageBox(parent_window, text, "error")
            # Return id and name of selected or highlighted row
            iid = self.tree_view.focus()
            name = self.tree_view.item(iid)['values'][0]
            index_ = self.list_of_children.index(iid)  # return the index of the iid in the list

            # Delete the wifi profile from tree view as well as from system
            self.tree_view.delete(iid)
            self.list_of_children.pop(index_)
            self.index_of_previous_item = ("", "", False)

            # Removes the Wi-Fi profile from the user system.
            command = 'netsh wlan delete profile name="' + name + '"'
            subprocess.run(command, shell=True, capture_output=True, text=True)

            # Remove the xml or text file also, which is saved in temp_ directory.
            text_file_name = str(sum([ord(i) for i in name]))
            if os.path.isfile(self.app_path + "\\temp_\\Wi-Fi-" + name + ".xml"):
                os.remove(self.app_path + "\\temp_\\Wi-Fi-" + name + ".xml")

            elif os.path.isfile(self.app_path + "\\temp_\\" + text_file_name + ".txt"):
                os.remove(self.app_path + "\\temp_\\" + text_file_name + ".txt")

            # When the selected row deleted, the below code decides where to move the focus next
            # means to select which row.
            if len(self.list_of_children) >= 1:
                if index_ == len(self.list_of_children):
                    index_ = index_ - 1
                self.tree_view.selection_set(self.list_of_children[index_])
                self.tree_view.focus(self.list_of_children[index_])

            # Pop-Up message to display that profile successfully deleted.
            text = "Successfully deleted."
            db.MessageBox(parent_window, text, "warning")

        except Exception:
            self.index_of_previous_item = ("", "", False)
            text = "Unable to delete. Software is facing several issue during deletion."
            db.MessageBox(parent_window, text, "error")


class GettingData:
    """ This is a helping class which will help WifiDisplayBox to call methods of SavedWifiInfo and
    reformat and parse some of the results return by methods of SavedWifiInfo.
    """

    def __init__(self, app_path):
        self.app_path = app_path
        self.wifi_information = saved_wifi_info.WifiInformation(self.app_path)
        self.headings_of_treeview = ['Wifi Name', 'SSID', 'Authentication', 'Password']

    def create_wifi_list(self):
        """ Return newly created wifi list."""
        self.wifi_information.generating_wifi_list()

    def get_headings(self):
        """ Return list of heading names """
        return self.headings_of_treeview

    def wifi_list(self):
        """ Return wifi data of specific profile in the form of
        ["name", "" ,"", ""]
        """
        return self.wifi_information.retrieving_list_of_wifi()

    def detailed_list(self, name):
        """ Return wifi data of specific profile in the form of
        ["name", "ssid" ,"authentication", "key"]
        """
        profile_detail = self.wifi_information.wifi_details(name)
        if profile_detail[-1] is None or profile_detail[-1] == "*None*":
            profile_detail[-1] = ""
        return profile_detail
