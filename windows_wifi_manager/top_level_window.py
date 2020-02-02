"""This module creates different top-level window, creates and placing widget and adding
functionality to the widgets. Every class defined here creates a different top level window
with different functionality and uses. Like one class 'QuitWindow' creates a top level window
and asking user if they really want to quit(like a message box). Some top-level widgets work
can easily be done by tkinter messagebox but due to position or geometry cannot be specified
explicitly and the message box (top-level window) created by some of this classes places the
window at the centre of the parent window (irrespective of what the size of the parent window
is."""
import os
import tkinter
import webbrowser
from abc import ABC, abstractmethod
from tkinter import ttk
from xml.dom import minidom

try:
    import lxml.etree as etree
except ImportError:
    import xml.etree.ElementTree as etree
import subprocess


class BasicDialog(tkinter.Toplevel, ABC):
    """ This is a base class of every top level window, it only defines the geometry
        of the top level window, move focus to top level window, provide basic design
        to the window and prevent user to access parent window until this top level window
        closes."""

    def __init__(self, parent, title=None):
        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)

        # Defines the position w.r.t to parent window, so that
        # top-level window will be in the middle of parent window
        #
        # The below x, y takes time for calculation(i.e., the reason for
        # flashes in top level window, but it is necessary because it guide
        # where to position the top level window as a reference to parent.
        # or some other functions is doing issue
        #
        x_coordinate = parent.winfo_rootx() + parent.winfo_width() // 2 - \
                       self.winfo_reqwidth() // 2  # x-coordinate
        y_coordinate = parent.winfo_rooty() + parent.winfo_height() // 2 - \
                       self.winfo_reqheight() // 2  # y-coordinate
        self.geometry("+%d+%d" % (x_coordinate, y_coordinate))
        self.configure(background='white')
        if title:
            self.title(title)
        self.iconbitmap(os.path.dirname(os.path.realpath(__file__)) + "/data/images/wifi2.ico")
        self.resizable(False, False)  # window cannot be resized
        self.temp = tkinter.BooleanVar()  # Defining Variable of type boolean
        self.parent = parent
        body_frame = tkinter.Frame(self, background='white')
        self.initial_focus = self.body(body_frame)  # setting focus to the frame ssid_entry
        body_frame.pack(padx=5, pady=5)
        self.button_box()
        self.grab_set()

        # set focus to either and widget or to the window itself
        if not self.initial_focus:
            self.initial_focus = self
        self.bind("<Button-1>", self.alarm)
        self.bind("<Button-3>", self.alarm)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.initial_focus.focus_set()
        self.wait_window(self)  # wait until top level closes

    def alarm(self, event):
        """ This function will capture the mouse click coordinate (both left or click)
            as respect to system screen and if the mouse click lies in parent window
            (not in top level window), it flashes out the top level window and the
             window bell will ring."""

        # top left corner of top level window
        x1_coordinate, y1_coordinate = self.winfo_rootx(), self.winfo_rooty()

        # bottom right corner of top level window
        x2_coordinate = x1_coordinate + self.winfo_width()
        y2_coordinate = y1_coordinate + self.winfo_height()
        if not (x1_coordinate < event.x_root < x2_coordinate and
                y1_coordinate < event.y_root < y2_coordinate):
            self.attributes("-alpha", 0.1)
            self.bell()
            self.after(100, lambda: self.attributes("-alpha", 1))

    @abstractmethod
    def body(self, _):
        """ Defines the widgets underlying in frame(_), and if possible returns the widget on
            which the focus had to be set."""
        return False

    def button_box(self):
        """ Create a new frame in top level window and add two buttons "OK" and
            "Cancel" which will call the 'ok' and 'cancel' method of this class resp.
             In many inherited class this function is override."""

        below_hz_frame = tkinter.Frame(self)
        ok_button = ttk.Button(below_hz_frame, text="OK",
                               width=10, command=self.ok,
                               default=tkinter.ACTIVE)
        ok_button.grid(row=0, column=0, padx=30, pady=10)
        cancel_button = ttk.Button(below_hz_frame, text="Cancel", width=10,
                                   command=self.cancel)
        cancel_button.grid(row=0, column=1, padx=30, pady=10)

        # bind 'ok' method to the 'enter' button of the keyboard
        self.bind("<Return>", self.ok)

        # bind 'cancel' method to the 'esc' button of the keyboard
        self.bind("<Escape>", self.cancel)
        below_hz_frame.pack(fill=tkinter.X)

    def ok(self, _=None):
        """ This will destroy the top level window and allow to do some task after user
            done their work before closing the window."""

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.temp.set(True)  # set boolean variable temp equal to True
        self.apply()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, _=None):
        """ This will destroy the top level window"""

        self.parent.focus_set()
        self.temp.set(False)  # set boolean variable temp equal to False
        self.destroy()

    @abstractmethod
    def validate(self):
        """ Validate the data, it is inherited in add_profile class."""
        return 1

    @abstractmethod
    def apply(self):
        """ Called after user successfully terminate the top-level window"""
        return


class QuitWindow(BasicDialog):
    """ This class will ask user if he/she really want to quit."""

    def __init__(self, parent):
        BasicDialog.__init__(self, parent, title=None)

    def body(self, master):
        path_dir = os.path.dirname(os.path.realpath(__file__))
        image_ssid_entry = tkinter.PhotoImage(file=path_dir + "/data/images/warning.png")
        image_label = tkinter.Label(master, image=image_ssid_entry, bg="white")
        image_label.image = image_ssid_entry
        text_label = tkinter.Label(master, text="Do you really wish to Quit?",
                                   bg="white", font=("Playfair Display", 12))
        image_label.grid(row=0, column=0, sticky="w", padx=5, pady=(8, 2))
        text_label.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=(8, 2))

    def validate(self):
        """ Validate the data, it is inherited in add_profile class."""
        return 1

    def apply(self):
        """ Called after user successfully terminate the top-level window"""
        return


class AddProfile(BasicDialog):
    """ In this the user had to enter all the valid details like
    SSID's, authentication, etc. to add wi-fi profile to the system."""

    def __init__(self, parent, app_path):
        """ All the string variable of the entry widget and combobox(drop-down list)
            are defined """
        self.app_path = app_path
        self.ssid = tkinter.StringVar()
        self.connection_mode = tkinter.StringVar()
        self.authentication = tkinter.StringVar()
        self.encryption = tkinter.StringVar()
        self.password = tkinter.StringVar()
        self.profile_data = []
        # calling constructor of base class.
        BasicDialog.__init__(self, parent, title=None)

    def body(self, master):

        self.ssid.set("")
        self.connection_mode.set("Auto")
        self.authentication.set("WPA2PSK")
        self.encryption.set("AES")
        self.password.set("")
        temp_text = "Not available for ad-hoc and WEP (only WPA and WPA2 personnel)"
        top_label = tkinter.Label(master, text=temp_text, background="white",
                                  font=("Playfair Display", 8, "bold"))
        self.ssid_label = tkinter.Label(master, text="SSID", background="white",
                                        font=("Playfair Display", 10))
        ssid_entry = ttk.Entry(master, cursor="xterm", textvariable=self.ssid, width=28)
        cm_label = tkinter.Label(master, text="Connection Mode", background="white",
                                 font=("Playfair Display", 10))
        cm_combo = ttk.Combobox(master, textvariable=self.connection_mode,
                                values=["Auto", "Manual"], state="readonly")
        auth_label = tkinter.Label(master, text="Authentication", background="white",
                                   font=("Playfair Display", 10))
        auth_combo = ttk.Combobox(master, textvariable=self.authentication,
                                  values=["WPA2PSK", "WPAPSK", "open"], state="readonly")
        encrypt_label = tkinter.Label(master, text="Encryption", background="white",
                                      font=("Playfair Display", 10))
        encrypt_combo = ttk.Combobox(master, textvariable=self.encryption,
                                     values=["AES", "TKIP"], state="readonly")
        self.pass_label = tkinter.Label(master, text="Password", background="white",
                                        font=("Playfair Display", 10))
        self.pass_entry = ttk.Entry(master, cursor="xterm", textvariable=self.password,
                                    show="*", width=28)
        top_label.grid(row=0, column=0, columnspan=2, padx=2, pady=(8, 2))
        self.ssid_label.grid(row=1, column=0, sticky="w", padx=5, pady=(8, 2))
        ssid_entry.grid(row=1, column=1, sticky="w", padx=(10, 5), pady=(8, 2))
        cm_label.grid(row=2, column=0, sticky="w", padx=5, pady=(8, 2))
        cm_combo.grid(row=2, column=1, sticky="w", padx=(10, 5), pady=(8, 2))
        auth_label.grid(row=3, column=0, sticky="w", padx=5, pady=(8, 2))
        auth_combo.grid(row=3, column=1, sticky="w", padx=(10, 5), pady=(8, 2))
        encrypt_label.grid(row=4, column=0, sticky="w", padx=5, pady=8)
        encrypt_combo.grid(row=4, column=1, sticky="w", padx=(10, 5), pady=(8, 2))
        self.pass_label.grid(row=5, column=0, sticky="w", padx=5, pady=8)
        self.pass_entry.grid(row=5, column=1, sticky="w", padx=(10, 5), pady=(8, 2))
        bottom_label = tkinter.Label(master, text="(You can use <Tab> key to communicate "
                                                  "between entry fields)", background="white",
                                     font=("Playfair Display", 8, "italic"))
        bottom_label.grid(row=6, column=0, columnspan=2, padx=2, pady=(8, 2))
        return ssid_entry

    def validate(self):
        """ Check if user entered the correct details and if not, warn user and protect them
            from moving them to next step."""

        # Check if user leaves the 'ssid' blank.
        if self.ssid.get() == "":
            self.ssid_label.configure(text="SSID*", foreground="red")
            return

        # If authentication is not open, then password should not
        # be empty and between 8 to 64 char.
        if self.authentication.get() != "open":
            self.ssid_label.configure(text="SSID", foreground="black")
            self.initial_focus = self.pass_entry
            if self.password.get() == "":
                self.pass_label.configure(text="Password(" + self.authentication.get() + ")*",
                                          foreground="red")
                return

            if not 8 <= len(self.password.get()) <= 63:
                self.pass_label.configure(text="Password(8 to 63)*", foreground="red")
                return

            if self.authentication.get() == "WPA2PSK":
                self.encryption.set("AES")

        # If Authentication is 'open' then the password should be ""
        # and encryption to be None.
        elif self.authentication.get() == "open":
            self.encryption.set("none")
            self.password.set("")

        self.pass_label.configure(text="Password", foreground="black")

        # Creating a list of user entered field (SSID's, etc.)
        self.profile_data.append(self.ssid.get())
        self.profile_data.append(self.connection_mode.get())
        self.profile_data.append(self.authentication.get())
        self.profile_data.append(self.encryption.get())
        self.profile_data.append(self.password.get())

        self.withdraw()  # hide the top-level window until another top-level closes.

        # Creates another top-level window over this top-level window(add_profile)
        result = AddProfile2(self.parent, self.profile_data)
        self.profile_data.clear()  # clear list

        # If everything ok then return 1
        # else move focus to previous top level window(add_profile).
        if result.temp.get():
            return 1
        self.initial_focus = self
        self.deiconify()  # show the top-level window(add_profile)

    def apply(self):
        """ Create xml file and add profile to system"""

        file_name = str(sum([ord(i) for i in self.ssid.get()]))

        def saving_file(xml):
            """ Save user profile in xml format to temp_ dir."""

            xml_string = etree.tostring(xml)
            parsed = minidom.parseString(xml_string)
            with open(self.app_path + "\\temp_\\" + file_name + ".xml", "w") as file:
                file.write(parsed.toprettyxml(indent="        "))

        parse_xml = etree.parse(os.path.dirname(os.path.realpath(__file__)) +
                                "/data/sampleProfile.xml")

        # The below code will parse the sample xml file
        # and fill important details entered by the user.
        root_tree = parse_xml.getroot()
        root_tree[0].text = self.ssid.get()
        root_tree[1][0][0].text = self.ssid.get()
        root_tree[3].text = self.connection_mode.get().lower()
        security = root_tree[4][0]
        security[0][0].text = self.authentication.get()
        security[0][1].text = self.encryption.get()
        if self.authentication.get() != "open":
            etree.SubElement(security, "sharedKey")
            etree.SubElement(security[1], "keyType").text = "passPhrase"
            etree.SubElement(security[1], "protected").text = "false"
            etree.SubElement(security[1], "keyMaterial").text = self.password.get()

        # Save the xml file
        saving_file(root_tree)

        # Add profile to the system.
        temp_path = 'netsh wlan add profile filename="' + self.app_path + "\\temp_\\"
        output_ = subprocess.run(temp_path + file_name + '.xml"', shell=True,
                                 capture_output=True, text=True)
        os.remove(self.app_path + "\\temp_\\" + file_name + ".xml")

        # If unable to add profile.
        if output_.returncode != 0:
            message = "Sorry, Unable to add profile.\n(You entered wrong details " \
                      "or else you don't have admin rights.)"
            image_ = "error"

        else:
            message = "Profile added successfully (Please Refresh)"
            image_ = "warning"

        MessageBox(self.parent, message, image_)


class AddProfile2(BasicDialog):
    """ This will display user entered details and wait for confirmation from user
        for further proceeding(ie., adding to system)"""

    def __init__(self, parent, profile_data):
        self.profile_data = profile_data  # list of user entered details
        BasicDialog.__init__(self, parent, title=None)

    def body(self, master):
        """ Create widgets to display user entered details"""

        def building_block(text_, row_no, column_no, color):
            """ Defining labels and packing."""
            temp = tkinter.Label(master, text=text_, font=("Playfair Display", 13),
                                 background="white", foreground=color)
            temp.grid(row=row_no, column=column_no, sticky="nw", padx=5, pady=(8, 2))

        building_block("SSID ", 0, 0, "red")
        building_block(":  '" + self.profile_data[0] + "'", 0, 1, "green")
        building_block("Connection Type ", 1, 0, "red")
        building_block(":  " + "ESS", 1, 1, "blue")
        building_block("Connection Mode ", 2, 0, "red")
        building_block(":  " + self.profile_data[1], 2, 1, "green")
        building_block("Authentication ", 3, 0, "red")
        building_block(":  " + self.profile_data[2], 3, 1, "green")
        building_block("Encryption ", 4, 0, "red")
        building_block(":  " + self.profile_data[3], 4, 1, "green")
        building_block("Key Type ", 5, 0, "red")
        building_block(":  " + "PassPhrase", 5, 1, "blue")
        building_block("Password: ", 6, 0, "red")
        building_block(":  '" + self.profile_data[4] + "'", 6, 1, "green")

    def validate(self):
        """ Validate the data, it is inherited in add_profile class."""
        return 1

    def apply(self):
        """ Called after user successfully terminate the top-level window"""
        return


class MessageBox(BasicDialog):
    """ Display message to user for success or error"""

    def __init__(self, parent, message, image_to_displayed=None):
        """ Text or image to be displayed"""

        self.text_ = message
        path_dir = os.path.dirname(os.path.realpath(__file__))
        if image_to_displayed == "warning":
            image_ = tkinter.PhotoImage(file=path_dir + "/data/images/warning.png")
        elif image_to_displayed == 'check':
            image_ = tkinter.PhotoImage(file=path_dir + "/data/images/check.png")
        else:
            image_ = tkinter.PhotoImage(file=path_dir + "/data/images/error.png")

        self.image_ = image_
        BasicDialog.__init__(self, parent, title=None)

    def body(self, master):

        image_label = tkinter.Label(master, image=self.image_, bg="white")
        image_label.image = self.image_
        message_label = tkinter.Label(master, text=self.text_, bg="white",
                                      font=("Playfair Display", 12))
        msg_for_user = "Software is under development. " \
                       "Contact developer for software related issues(check 'About')."
        imp_msg = tkinter.Label(master, text=msg_for_user, bg="white",
                                font=("Playfair Display", 8, "italic"))
        image_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=5, pady=(8, 2))
        message_label.grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(8, 2))
        imp_msg.grid(row=1, column=1, sticky="w", padx=(0, 5), pady=(8, 2))

    def button_box(self):

        below_hz_frame = tkinter.Frame(self)
        ok_button = ttk.Button(below_hz_frame, text="OK", width=10,
                               command=self.ok, default=tkinter.ACTIVE)
        self.bind("<Return>", self.ok)
        ok_button.pack(side=tkinter.RIGHT, padx=15, pady=5)
        below_hz_frame.pack(fill=tkinter.X)

    def validate(self):
        """ Validate the data, it is inherited in add_profile class."""
        return 1

    def apply(self):
        """ Called after user successfully terminate the top-level window"""
        return


class About(BasicDialog):
    """ This class designs the About top-level window, it opens when
    the user user click on 'About' in menu bar in Application main window.
    """

    def __init__(self, parent):
        """ Designing the basic top level window"""

        BasicDialog.__init__(self, parent, title=None)

    def body(self, master):

        def link_click(_):
            """ Detects the tag and open the link."""

            tag_name = about_content.tag_names(tkinter.CURRENT)[0]
            about_content.tag_config(tag_name, foreground="#551A8B")
            if tag_name == 'hyper':
                webbrowser.open("https://www.facebook.com/nihal.agarwal.14")
            else:
                webbrowser.open("https://github.com/NihalAgarwal/Windows-Wi-Fi-Manager")

        def mouse_in(event):
            """ Changing the cursor if use place cursor on link."""

            if str(event.type) == 'Enter':
                about_content.config(cursor="hand2")
            else:
                about_content.config(cursor="arrow")

        about = "This is my winter holidays project which I am sharing with you all. Hope, you" \
                " understood what the Application does. It allows you to look at your saved WiFi" \
                " profile and their details (SSID, Authentication and key) of your system. I know" \
                " you can do it manually by using CMD but rather than typing 'netsh.' and search" \
                " for the profile in odd-looking CMD with complex and not memorizable command" \
                " you can do it by just running ‘.exe’ file of this Application and see the" \
                " list of all saved WiFi profile in sorted order in table form. You can also" \
                " delete the saved Wi-Fi profile from your system and most important you can" \
                " also add the 'Wi-Fi name' and 'passkey' of anyone's Wi-Fi and when your system" \
                " is in a range of that Wi-Fi, it gets connected to that network.\n" \
                "For more info go to my project GitHub page (link below)."

        # text widget 1 for about the Application does
        about_content = tkinter.Text(master, background="#107896",
                                     foreground="white", cursor='arrow', wrap=tkinter.WORD, padx=10)

        # specifying styles for different text
        about_content.tag_configure('bold_italics', foreground="black",
                                    font=('Arial', 12, 'bold', 'italic', 'underline'))
        about_content.tag_configure('normal', font=('Arial', 12), spacing2=0.5)
        about_content.tag_configure('normal1', font=('Arial', 12), foreground="red")
        about_content.tag_configure('hyper', font=('Arial', 12),
                                    underline=1, foreground="#0000FF")
        about_content.tag_configure('hyper1', font=('Arial', 12),
                                    underline=1, foreground="#0000FF")

        # binding event for mouse pointer
        about_content.tag_bind("hyper", "<Button-1>", link_click)
        about_content.tag_bind("hyper", "<Enter>", mouse_in)
        about_content.tag_bind("hyper", "<Leave>", mouse_in)
        about_content.tag_bind("hyper1", "<Button-1>", link_click)
        about_content.tag_bind("hyper1", "<Enter>", mouse_in)
        about_content.tag_bind("hyper1", "<Leave>", mouse_in)

        about_content.insert(tkinter.END, "\nAbout\n\n", "bold_italics")
        about_content.insert('end', about, "normal")

        # Adding contact information
        about_content.insert(tkinter.END, "\n\nContact\n\n", "bold_italics")

        email_info = "nihal.agarwal.1426@gmail.com\n\n"
        facebook_info = "www.facebook.com/nihal.agarwal.14"
        github_info = "https://github.com/NihalAgarwal/Windows-Wi-Fi-Manager"

        about_content.insert('end', " Email : ", 'normal1')
        about_content.insert('end', email_info, 'normal')

        about_content.insert('end', " Follow on Facebook : ", 'normal1')
        about_content.insert('end', facebook_info, 'hyper')
        about_content.insert('end', "\n\n", 'normal')

        about_content.insert('end', " Send Fork Request : ", 'normal1')
        about_content.insert('end', github_info, 'hyper1')
        about_content.insert('end', "\n\n", 'normal')

        about_content.config(state=tkinter.DISABLED)
        about_content.pack(side="top", padx=2, pady=2)

    def button_box(self):
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def validate(self):
        """ Validate the data, it is inherited in add_profile class."""
        return 1

    def apply(self):
        """ Called after user successfully terminate the top-level window"""
        return


# For testing purpose
if __name__ == "__main__":
    def check_function():
        """ Call the objects method or create
        instance to check the functionality of
        any top-level widget.
        """
        About(ROOT)
        # quit_or_not(root)


    ROOT = tkinter.Tk()
    ROOT.geometry('900x500')
    ttk.Button(ROOT, text="Check", command=check_function, default=tkinter.ACTIVE).pack()
    ROOT.mainloop()
