""" This script file is responsible to return the check whether system is
connected to any Wi-Fi network and return SSID name and also give functionality
to disconnect from the current connected network.
"""
import re
import subprocess

from windows_wifi_manager.top_level_window import MessageBox


class SystemWifiConnection:
    """ Check system is connected to any Wi-Fi network and also the functionality
    of disconnect and refresh(to check whether system is connected to any network or
    not.
    """

    def __init__(self, parent):
        """ Declare ssid_name, interface_name(Wi-Fi), parent(reference to parent window
        which is used to display error pop-up message.
        """

        self.parent = parent
        self.interface_name = None
        self.ssid_name = None

    def is_connected(self):
        """ Check if system is connected to any Wi-Fi network. If true,
        return ssid_name and interface name else return None.
        """

        command = 'netsh wlan show interfaces | findstr "Name State SSID"'
        output = subprocess.run(command, shell=True, capture_output=True, text=True)
        my_regex = r"Name.*?connected.*?(?= *BSSID)"
        network_status = re.search(my_regex, output.stdout, re.DOTALL)

        if network_status is None:
            return None
        network_status = network_status.group()
        self.interface_name = re.findall(r"[\n\r-<>():]?.*Name\s*: ([^\n\r]*)", network_status)[0]
        self.ssid_name = re.findall(r"[\n\r-<>():]?.*SSID\s*: ([^\n\r]*)", network_status)[0]
        return self.ssid_name

    def disconnect_connection(self):
        """ Disconnects if system is connected to any Wi-Fi network"""

        command = 'netsh wlan disconnect interface = "' + self.interface_name + '"'
        output = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if system is disconnected from network successfully.
        if output.returncode != 0:
            message = "Sorry, unable to disconnect"
            MessageBox(self.parent, message, "error")  # Display message of error.
            return False
        return True

    # WARNING
    # There is a bug in below function i.e., when user disconnect and reconnect to same network
    # and network is not available anymore. It still shows the result that connection to same
    # network is done successfully. It is a bug of 'command prompt'.
    def reconnect_network(self):
        """ Try to reconnect to same network. """
        command = 'netsh wlan connect name="' + self.ssid_name + '" interface = "' \
                  + self.interface_name + '"'
        output = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if system reconnect to same network successfully.
        if output.returncode != 0:
            message = "Unable to reconnect(either previous network is not available" \
                      " in range or profile is deleted)"
            MessageBox(self.parent, message, "error")  # Display message of error.
            return False
        return True
