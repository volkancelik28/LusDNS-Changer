from tkinter import *
from tkinter.ttk import Progressbar
from tkinter.ttk import Combobox
from tkinter.ttk import Notebook
from tkinter.ttk import Treeview
from PIL import Image, ImageTk
import tkinter.font
from tkinter import ttk, messagebox
import subprocess

DNS_SERVERS = [
    ("CloudFlare DNS", "1.1.1.1", "1.0.0.1"),    
    ("OpenDNS", "208.67.222.222", "208.67.220.220"),    
    ("Google Public DNS", "8.8.8.8", "8.8.4.4"),    
    ("Quad9", "9.9.9.9", "149.112.112.112"),    
    ("Comodo SecureDNS", "8.26.56.26", "8.20.247.20"),    
    ("OpenDNS Family Shield", "208.67.222.123", "208.67.220.123"),
    ("Verisign", "64.6.64.6", "64.6.65.6"),
    ("Yandex Basic", "77.88.8.8", "77.88.8.1"),
    ("Yandex Safe", "77.88.8.88", "77.88.8.2"),
    ("Yandex Family", "77.88.8.7", "77.88.8.3"),
    ("AdGuard", "176.103.130.130", "176.103.130.131"),
    ("CleanBrowsing Security", "185.228.168.168", "185.228.169.9"),
]

def ping_dns(dns):
    cmd = f"ping {dns} -n 1"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = result.stdout.decode('utf-8')
    if "TTL" in output:
        time = output.split("time=")[1].split("ms")[0].strip()
        return time
    else:
        return "-"

def find_fastest_dns():
    fastest_time = float('inf')
    fastest_dns = None
    for dns in DNS_SERVERS:
        primary_dns = dns[1]
        secondary_dns = dns[2]
        primary_time = ping_dns(primary_dns)
        secondary_time = ping_dns(secondary_dns)
        if primary_time != "-" and secondary_time != "-":
            avg_time = (float(primary_time) + float(secondary_time)) / 2
            if avg_time < fastest_time:
                fastest_time = avg_time
                fastest_dns = dns
    return fastest_dns

def set_dns(dns):
    primary_dns = dns[1]
    secondary_dns = dns[2]
    wifi_interface = "Wi-Fi"
    ethernet_interface = "Ethernet"
    cmd_wifi = f"netsh interface ip set dns name=\"{wifi_interface}\" static {primary_dns} primary"
    cmd_ethernet = f"netsh interface ip set dns name=\"{ethernet_interface}\" static {primary_dns} primary"
    result = subprocess.run(cmd_wifi, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        result = subprocess.run(cmd_ethernet, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    cmd_wifi = f"netsh interface ip add dns name=\"{wifi_interface}\" {secondary_dns} index=2"
    cmd_ethernet = f"netsh interface ip add dns name=\"{ethernet_interface}\" {secondary_dns} index=2"
    result = subprocess.run(cmd_wifi, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        result = subprocess.run(cmd_ethernet, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

class LusDNS:
    def __init__(self, parent):
        self.gui(parent)
        self.disable_resizing()
        self.set_window_position()
        
    def set_window_position(self):
        width = 680
        height = 470
        screen_width = self.w1.winfo_screenwidth()
        screen_height = self.w1.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.w1.geometry(f"{width}x{height}+{x}+{y}")

        
    def disable_resizing(self):
        self.w1.resizable(False, False)
        
    def gui(self, parent):
        if parent == 0:
            self.w1 = Tk()
            self.w1.geometry('680x470')
            self.w1.title("LusDNS")
        else:
            self.w1 = Frame(parent)
            self.w1.place(x=0, y=0, width=680, height=470)
        self.group1 = LabelFrame(self.w1, text="DNS Servers :", font=tkinter.font.Font(family="Poppins", size=9),
                                 cursor="arrow")
        self.group1.place(x=30, y=80, width=620, height=270)
        self.lbl_title = Label(self.w1, text = "LUSDNS CHANGER", anchor='w', font = tkinter.font.Font(family = "Poppins", size = 20, weight = "bold"), cursor = "arrow", state = "normal")
        self.lbl_title.place(x = 220, y = 20, width = 260, height = 42)
        self.tree1 = Treeview(self.group1, columns=("DNS Name", "Primary DNS", "Secondary DNS", "Ping Time"))
        self.tree1.heading("#0", text="No.")
        self.tree1.heading("#1", text="DNS Name")
        self.tree1.heading("#2", text="Primary DNS")
        self.tree1.heading("#3", text="Secondary DNS")
        self.tree1.heading("#4", text="Ping Time")
        self.tree1.column("#0", width=40, anchor="center", stretch=False)
        self.tree1.column("#1", width=200, stretch=False)
        self.tree1.column("#2", width=120, stretch=False)
        self.tree1.column("#3", width=120, stretch=False)
        self.tree1.column("#4", width=100, anchor="center",stretch=False)
        self.tree1.place(x=10, y=10, width=600, height=220)

        
        index = 1
        for dns in DNS_SERVERS:
            primary_dns = dns[1]
            secondary_dns = dns[2]
            primary_time = ping_dns(primary_dns)
            secondary_time = ping_dns(secondary_dns)
            self.tree1.insert(parent='', index='end', iid=index, values=(dns[0], primary_dns, secondary_dns, primary_time))
            index += 1


        fastest_dns = find_fastest_dns()
        self.lbl_dns = Label(self.w1, text="Fastest DNS:", anchor='w',
                     font=tkinter.font.Font(family="Poppins", size=10, weight="bold"), cursor="arrow",
                     state="normal")
        self.lbl_dns.place(x=240, y=360, width=90, height=32)
        self.lbl_fast_dns = Label(self.w1, text=fastest_dns[0], anchor='w', font=tkinter.font.Font(family="Poppins", size=10),
                          cursor="arrow", state="normal")
        self.lbl_fast_dns.place(x=330, y=360, width=270, height=32)

        self.btn_change = Button(self.w1, text="Change DNS",
                                 font=tkinter.font.Font(family="Poppins", size=10, weight="bold"), cursor="arrow",
                                 state="normal", command=self.change_dns)
        self.btn_change.place(x=280, y=410, width=130, height=42)

    
    def change_dns(self):
        fastest_dns = find_fastest_dns()
        set_dns(fastest_dns)
        self.lbl_fast_dns.configure(text=fastest_dns[0])
        messagebox.showinfo("Info", "DNS Change Successful")

if __name__ == '__main__':
    a = LusDNS(0)
    a.w1.mainloop()
