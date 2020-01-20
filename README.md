<h1 align="center">Windows Wi-Fi Manager</h1>
<p align="center">Get saved Wi-Fi details (including key) and add a Wi-Fi without connecting to it. So when Wi-Fi is under range your OS (or system) will automatically set up the connection.</p>

<p align="center">
   <img src="https://raw.githubusercontent.com/NihalAgarwal/Windows-Wi-Fi-Manager/master/images/image1.png" width='650' height='500'>
</p>

## Getting Started

### Prerequisites
 - Python : Python >= 3.3 ( including 3.7 🎉 )
 - Windows Operating System (for others OS work is still in development)

*The Application is made only for Window users, .exe file or setup file will be uploaded as soon as possible.*

### Installation and Usage
#### Installing Via [PyPI](https://pypi.org/project/windows-wifi-manager/)
You can install this project using PyPI:
```
> pip install windows-wifi-manager
```
Then to run it, execute the following in the terminal:
```
> windows-wifi-manager
```

### Installing Via [GitHub](https://github.com/NihalAgarwal/Windows-Wi-Fi-Manager)
```
> git clone https://github.com/NihalAgarwal/Windows-Wi-Fi-Manager.git
> cd Windows-Wi-Fi-Manager
> python setup.py install
```
Then to run it, execute the following in the terminal:
```
> windows-wifi-manager
```


## About this Application

This Desktop Application finds out all the saved Wi-Fi from your window system and displays the **Wi-Fi details of specific Wi-Fi profile (SSID name, Authentication, Password).** I know it is simple to get the password by just using CMD and typing commands like *netsh wlan show profile name = "\<profile name>" key=clear"* but that's not everyone is familiar with and you have to manually type the SSID name of that Wi-Fi profile and for some profile like _**Mr.N=**_ you will get the result as _**“Mr.N=key=clear" is not found on the system**_. The issue with this profile is '__=__' at the end of the SSID name, did you ever think if some SSID's contain emoji's how will you type it in CMD ( ' ', " ", :, etc. If these types of symbols are present in SSID name, then also it is very difficult) but we know that nothing is impossible, you can suppress this problem by using _escape characters like \\ or ^ to escape characters like "" and '' and many more_, **but this Application will list out all the saved Wi-Fi in sorted order and you just had to scroll down and choose the name of the Wi-Fi of whom you want to get the details and you will get all information of that profile including Security Key (Password).**

![Wi-Fi detail of slected profile](https://raw.githubusercontent.com/NihalAgarwal/Windows-Wi-Fi-Manager/master/images/image2.png)

The other benefit of this application is that **you can manually save the SSID name, Authentication, and Password of any Wi-Fi profile** and when your system comes under that Wi-Fi range, it will automatically get connected to that Wi-Fi network. For example, If you know someone’s Wi-Fi details and that Wi-Fi is not in the range and your system is never connected to it before, then you can use this application and select the **_'Add Profile'_** option and then enter the details of that Wi-Fi profile, confirm it and details of that Wi-Fi profile will saved to your system and one day when your system detects the frequency of that Wi-Fi (or getting signals from that Wi-Fi Network) _it will automatically get connected, rather than asking for a password for the first time connection establishment_ (like we do for the first time when connecting to any Wi-Fi Network).

![Adding Wi-Fi profile](https://raw.githubusercontent.com/NihalAgarwal/Windows-Wi-Fi-Manager/master/images/image3.png)

*If your system is flooded with too much of Wi-Fi profiles*, going to CMD and selecting the SSID name by typing '_netsh wlan show profiles_' and then selecting the profile and then use delete command with manually typing the SSID name and some time it doesn’t get successful like I mention above that **some SSID’s contain ambiguous name (like containing symbols, emojis within their name)** and it is very difficult for CMD to parse the command and find out the SSID name but in **_Windows Password Manager_** you can delete it in one click by selecting the Wi-Fi profile in the list and press delete button.

![Successfully deleted a profile](https://raw.githubusercontent.com/NihalAgarwal/Windows-Wi-Fi-Manager/master/images/image4.png)

<p>If you are still having any confusion, give a try to Application and you will definitely know what I mean to say above.</p>

## Issues
<p>The Application is under developement, mail me if you are facing any issue and want to give any suggestion, feel free to mail me..</p>

**Mail id** = nihal.agarwal.1426@gmail.com

## Contribute
<p> The Application is under developement, if anyone wants to contribute in development feel free to send fork request to me.

#### THANK YOU!🙂
