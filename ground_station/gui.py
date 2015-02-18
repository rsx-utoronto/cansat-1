'''
Ground Station Framework (Rover and CanSat Projects)
Robotics for Space Exploration, University of Toronto (Canada)
University of Toronto Institute for Aerospace Studies (UTIAS)
Made by: Rahul Goel - rahul.g.eng@gmail.com

Install the necessary modules in the following order (if running into problems, uninstall and reinstall in this order for correct build):

sudo apt-get install tk tk-dev
pip install matplotlib

'''

import Tkinter as tk
from Tkinter import *
from serial import *
import ttk, user, sys, time, datetime, thread
from subprocess import check_output
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

root = tk.Tk()

ser = None
baud_rate = 57600
ser_connected = False

def key(event):
    root.status.set(repr(event.char)) 

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        filemenu = tk.Menu(self, tearoff = False)
        self.add_cascade(label="File",underline = 0, menu = filemenu)
        filemenu.add_command(label = "Save Data (.csv)", command=self.callback)
        filemenu.add_separator()
        filemenu.add_command(label = "Start", command = self.callback)
        filemenu.add_command(label = "Pause", command = self.callback)
        filemenu.add_command(label = "Stop", command = self.callback)
        filemenu.add_separator()                
        filemenu.add_command(label = "Exit", underline = 1, command = self.quit)

        filemenu = tk.Menu(self, tearoff = False)
        self.add_cascade(label = "Establish Connection", underline = 0, menu = filemenu)

        found_port = False
        for port in check_output(["ls", "/dev"]).split("\n"):
            if port.find("USB") != -1:
                found_port = True
                port_str = str(port)
                filemenu.add_command(label = port, command = lambda: self.open_ser(port_name = port_str))

        filemenu.add_command(label = "Disconnect", command = self.callback)

        if not found_port:
            filemenu.add_command(label = "No COM Device Found")

        helpmenu = tk.Menu(self, tearoff = False)
        self.add_cascade(label = "Help", menu = helpmenu)
        helpmenu.add_command(label = "About", command = self.callback)

    def quit(self):
        sys.exit(0)
    
    def callback(self, text = "foo"):
        print "called the callback!"
        print text

    def open_ser(self, port_name = None):
        global ser, ser_connected
        
        try:
            ser = Serial("/dev/%s" % port_name, baud_rate, timeout = 0, writeTimeout = 0)
            root.status.set("Connected to %s" % port_name)
            ser_connected = True

        except Exception as e:
            root.status.set("Error: Connection could not be established. %s" % e)

class StatusBar(ttk.Frame):

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.label = ttk.Label(self, relief='sunken', anchor='w')
        self.label.pack(fill='x')
        self.set("Waiting to connect")

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

def plot_altitude(location):

    f = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot = FigureCanvasTkAgg(f, master = location)
    data = [1, 2, 7, 1, 5, 4, 13, 8, 4, 10]

    a = f.add_subplot(111)
    a.plot(data)

    a.set_title("Altitude (m)")
    dataPlot.show()
    dataPlot.get_tk_widget().pack()

    '''
    for i in range(0, 5):
        f.clf()
        a = f.add_subplot(111)
        data.append(i)
        a.plot(data)

        a.set_title("sfw")
        dataPlot.show()
        dataPlot.get_tk_widget().pack()

        time.sleep(1)
    '''

def plot_temperature(location):

    f = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot = FigureCanvasTkAgg(f, master = location)
    x_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    outside_temp = [25, 22, 25, 26, 25, 23, 23, 25, 25, 24]
    inside_temp = [27, 28, 27, 25, 25, 26, 27, 28, 24, 30]

    a = f.add_subplot(111)
    a.plot(x_axis, outside_temp, "r", label = "Outside")
    a.plot(x_axis, inside_temp, "b", label = "Inside")

    a.set_title("Temperature (C)")
    a.set_ylim([-40, 40])
    legend = a.legend(loc='lower right', shadow=True)

    dataPlot.show()
    dataPlot.get_tk_widget().pack()

def plot_voltage(location):

    f = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot = FigureCanvasTkAgg(f, master = location)
    voltage = 6.5

    a = f.add_subplot(111)

    if voltage > 7.5:
        a.bar(0, voltage, 1, color = 'g')
    elif voltage > 5.5:
        a.bar(0, voltage, 1, color = 'y')
    else:
        a.bar(0, voltage, 1, color = 'r')

    a.set_title("Voltage (V)")
    a.set_ylim([0, 10])
    a.get_xaxis().set_visible(False)

    dataPlot.show()
    dataPlot.get_tk_widget().pack()    

def plot_acc(location):

    f = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot = FigureCanvasTkAgg(f, master = location)
    acc_x = 250
    acc_y = -187
    acc_z = -360

    a = f.add_subplot(111)

    a.bar(0, acc_x, 1, color = 'g')
    a.bar(1, acc_y, 1, color = 'b')
    a.bar(2, acc_z, 1, color = 'r')

    a.set_title("Acceleration (x, y, z)")
    a.set_ylim([-500, 500])
    a.get_xaxis().set_visible(False)

    dataPlot.show()
    dataPlot.get_tk_widget().pack()   

def ser_test_write():
    global ser, ser_connected

    if ser_connected:
        ser.write("testing")
        print "testing"

    root.after(1000, ser_test_write)

def conclude():
    frame.focus_set()


### Setting up the layout ###

root.config(menu=MenuBar(root))
root.geometry("1000x600+200+50")
root.title("RSX CanSat Control Center Version 1.0")
#root.configure(background='white')

# Top info bar (team, time, flight status)

top_info_frame = Frame(root)
top_info_frame.pack(side = "top", pady = 20, fill = X)

label_top1 = Label(top_info_frame, text = "TEAM #1171")
label_top1.pack(side=LEFT, expand = 1, fill = X)
label_top2 = Label(top_info_frame, text = "Mission Time: %s" % str(datetime.datetime.now()))
label_top2.pack(side=LEFT, expand = 1, fill = X)
label_top2 = Label(top_info_frame, text = "Flight Status: Ascending")
label_top2.pack(side=LEFT, expand = 1, fill = X)

# Main chart area

frame = Frame(root, padx = 10, pady = 10)
frame.pack(side='top', fill='both')
frame.bind("<Key>", key)
frame.focus_set()

chart_width = (frame.winfo_width() - 40) / 4
chart_height = frame.winfo_height() / 2

chart1_frame = Frame(frame, bg = "white", width = chart_width, height = chart_height)
chart1_frame.grid(column = 0, row = 0)
chart2_frame = Frame(frame, bg = "white", width = chart_width, height = chart_height)
chart2_frame.grid(column = 1, row = 0)
chart3_frame = Frame(frame, bg = "white", width = chart_width, height = chart_height)
chart3_frame.grid(column = 2, row = 0)
chart4_frame = Frame(frame, bg = "white", width = chart_width, height = chart_height)
chart4_frame.grid(column = 3, row = 0)

# Top info bar (team, time, flight status)

stream_frame = Frame(root, bg = "white")
stream_frame.pack(side = "top", pady = 0, fill = BOTH, expand = True)

scrollbar = Scrollbar(stream_frame)
scrollbar.pack(side = RIGHT, fill = Y)

listbox = Listbox(stream_frame, width = 600, yscrollcommand=scrollbar.set)
f = open('../sample_data_file.csv', 'r')
for line in f:
    listbox.insert(0, str(line))
listbox.pack(side = LEFT, fill = BOTH)

scrollbar.config(command=listbox.yview)

# Bottom status bar

root.status = StatusBar(root)
root.status.pack(side='bottom', fill='x')

# Code to run after mainloop

root.after(0, plot_altitude(chart1_frame))
root.after(0, plot_temperature(chart2_frame))
root.after(0, plot_voltage(chart3_frame))
root.after(0, plot_acc(chart4_frame))

root.after(1000, ser_test_write)
root.after(1000, conclude)

root.mainloop()