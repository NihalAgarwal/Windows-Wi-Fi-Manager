"""This module takes the name of the profile and return the Wi-Fi details like SSID name,
Authentication and Key. Generating the Saved Wi-Fi details of some special SSID's gives a
problem. For a different type of SSID name, like some SSID name contain 'emojis' while some
contain special symbols which create a lot of problems when dealing with command prompt. So,
generating XML file of the per profile doesn't resolve some problem but not all. Some SSID's
like 'Redm"i=" are still creating problems.
"""

import os
import re
import subprocess
import xml.etree.ElementTree as etree


class WifiInformation:
    """ This class generates and return the SSID, Authentication, Key
    for the Wi-Fi profile as given as input.
    """

    def __init__(self, app_path):

        """
            This method is used to check if the necessary folder, file is present,
        otherwise create it. Also, initialize object variables.
        """

        self.app_path = app_path

        if not os.path.isdir(self.app_path + "\\temp_"):
            os.mkdir(self.app_path + "\\temp_")

        if os.path.isfile(self.app_path + "/Saved Wifi list.txt"):
            os.remove(self.app_path + "/Saved Wifi list.txt")
            self.generating_wifi_list()

        else:
            self.generating_wifi_list()

    def generating_wifi_list(self):
        """ Generates the list of Wi-Fi saved in you system and save it in parent folder of temp_.
        """

        with open(self.app_path + "/Saved Wifi list.txt", "w") as file:

            output = subprocess.run("netsh wlan show profile", shell=True,
                                    capture_output=True, text=True)

            # Parsing and finding required information and saving it into the file.
            if output.returncode == 0:
                my_regex = r"[\n\r-<>():].*All User Profile\s*: ([^\n\r]*)"
                list_of_wifi = re.findall(my_regex, output.stdout)
                list_of_wifi.sort(key = lambda x: x.lower())
                for i in list_of_wifi:
                    file.write(i + "\n")

    def retrieving_list_of_wifi(self):
        """ The below code returns list of tuple in the form of [(name, "", "", ""),].
        """

        list_of_wifi_detail = []
        with open(self.app_path + "/Saved Wifi list.txt", 'r') as file:
            wifi_detail = file.readlines()
            for item in wifi_detail:
                list_of_wifi_detail.append((item[:-1], "", "", ""))
        return list_of_wifi_detail

    def wifi_details_(self, name, text_file_name, wifi_detail):
        """ Called if XML or text file for particular wifi doesn't exist.
         It tries another possible way to retrieve information.
         """

        # Getting information for specific profile using
        # netsh wlan show profile name= "name" key =clear
        # then using findstr to search
        cmd = 'netsh wlan show profile name="' + name + \
              '" key=clear | findstr "Name name Authentication Key"'
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # If command executed successfully.
        if output.returncode == 0:
            ssid_regex = r"[\n\r-<>():].*Name\s*: ([^\n\r]*)"
            ssid_name = re.findall(ssid_regex, output.stdout)[0]
            authentication_regex = r"[\n\r-<>():].*Authentication\s*: ([^\n\r]*)"
            authentication = re.findall(authentication_regex, output.stdout)[0]

            if authentication == "Open":
                key_content = "None"
            else:
                key_content_regex = r"[\n\r-<>():].*Key Content\s*: ([^\n\r]*)"
                key_content = re.findall(key_content_regex, output.stdout)[0]

            return self.data_saving(text_file_name, ssid_name, authentication,
                                    key_content, wifi_detail)

        # THIS LAST OPTION DOESN'T PROVIDE THE KEY FOR WIFI. IT ONLY PROVIDE SSID's
        # AND AUTHENTICATION BECAUSE 'netsh wlan show profile * key=clear' PROVIDES
        # EVERYTHING FOR SPECIFIC PROFILE EXCEPT KEY. THE BELOW CODE IS USED TO RETRIEVE
        # INFORMATION FOR SSID's LIKE "Red"mi=", "abc:>gh=", etc. IF ANY ONE CAN SOLVE
        # THE ISSUE THEN YOU CAN BY REMOVING THE CODE FROM ELSE BLOCK AND PUT YOUR OWN
        # CODE, BUT DON'T REMOVE THE RETURN STATEMENT.

        try:
            cmd = 'netsh wlan show profile * key =clear | findstr ' \
                  '"Name name Authentication Key"'
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if output.returncode != 0:
                raise Exception
            my_regex = name + r".*?(?=Name)"
            info_of_ssid = re.findall(my_regex, output.stdout, re.DOTALL)[0]
            ssid_name_regex = r"[\n\r-<>():].*SSID name\s*: ([^\n\r]*)"
            ssid_name = re.findall(ssid_name_regex, info_of_ssid)[0]
            authentication_regex = r"[\n\r-<>():].*Authentication\s*: ([^\n\r]*)"
            authentication = re.findall(authentication_regex, info_of_ssid)[0]
            key_content = "*Unable to find*"

        except Exception:
            ssid_name = name
            authentication = "*Unable to find*"
            key_content = "*Unable to find*"

        return self.data_saving(text_file_name, ssid_name, authentication,
                                key_content, wifi_detail)

    @staticmethod
    def xml_parsing(tree, wifi_detail):
        """Parsing XML file to retrieve ssid, authentication and key(if any).
        """

        root = tree.getroot()
        namespace = re.match(
            r"{[^\s\n\r]+}", root.tag).group()

        ssid = tree.find(".//" + namespace + "SSID")
        ssid = ssid.find(".//" + namespace + "name")
        wifi_detail.append(ssid.text)
        authentication = tree.find(".//" + namespace + "authentication")
        wifi_detail.append(authentication.text)
        if authentication.text != "open":
            key_content = tree.find(".//" + namespace + "keyMaterial")
            wifi_detail.append(key_content.text)
        else:
            wifi_detail.append(None)

        return wifi_detail

    def wifi_details(self, name):
        """ Using the 'name' parameter find the profile and check every possible way
        to retrieve SSID, authentication and key(if any).
        """

        wifi_detail = [name]
        text_file_name = str(sum([ord(i) for i in name]))

        # if xml file of particular wifi profile is there in temp folder
        if os.path.isfile(self.app_path + "\\temp_\\Wi-Fi-" + name + ".xml"):
            tree = etree.parse(self.app_path + "\\temp_\\Wi-Fi-" + name + ".xml")

            return self.xml_parsing(tree, wifi_detail)

        # if text file of particular wifi profile is there in temp folder
        elif os.path.isfile(self.app_path + "\\temp_\\" + text_file_name + ".txt"):
            return self.data_retrieval(text_file_name, wifi_detail)

        else:
            # export all profile data into their specified xml file and save
            # to specific folder which is path to temp_ folder

            cmd = 'netsh wlan export profile key=clear folder="' + self.app_path + '\\temp_"'
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if output.returncode != 0:
                return self.wifi_details_(name, text_file_name, wifi_detail)

            # If xml file of particular wifi profile is there in temp folder
            elif os.path.isfile(self.app_path + "\\temp_\\Wi-Fi-" + name + ".xml"):
                tree = etree.parse(self.app_path + "\\temp_\\Wi-Fi-" + name + ".xml")
                return self.xml_parsing(tree, wifi_detail)

            return self.wifi_details_(name, text_file_name, wifi_detail)

    def data_retrieval(self, text_file_name, wifi_detail):
        """ Getting SSID name, authentication and password from the text file."""

        with open(self.app_path + "\\temp_\\" + text_file_name + ".txt", "r") as file:
            wifi_detail.append(file.readline()[:-1])
            auth_temp = file.readline()[:-1]
            wifi_detail.append(auth_temp)
            if auth_temp != "*None*":
                wifi_detail.append(file.readline()[:-1])
            else:
                wifi_detail.append(None)
            return wifi_detail

    def data_saving(self, text_file_name, ssid, authentication, key, wifi_detail):
        """ Saving SSID name, authentication and password to text file."""

        with open(self.app_path + "\\temp_\\" + str(text_file_name) + ".txt", "w") as file:
            file.writelines(ssid.strip('""') + "\n")
            file.writelines(authentication + "\n")
            wifi_detail.append(ssid.strip('""'))
            wifi_detail.append(authentication)
            if authentication != "Open" or authentication != "open":
                file.writelines(key + "\n")
                wifi_detail.append(key)
            else:
                file.writelines("*None*" + "\n")
                wifi_detail.append(None)

        return wifi_detail


# used for testing
if __name__ == "__main__":
    PATH = "C:\\Users\\Nihal\\AppData\\Local\\NihalAgarwal\\SavedPasswordFinder"
    OBJ1 = WifiInformation(PATH)
    # Display the list of tuple in the form of [('name', "", "", ""),]
    print(OBJ1.retrieving_list_of_wifi())
    # Display the list of detail for the given wifi.
    print(OBJ1.wifi_details("mr. n="))
