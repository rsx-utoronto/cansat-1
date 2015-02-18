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

data_altitude = [0]
data_temp_outside = [0.0]
data_temp_inside = [0.0]
data_voltage = [0.0]
data_state = []
data_acc_x = [0.0]
data_acc_y = [0.0]
data_acc_z = [0.0]  

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

        print port_name

        try:
            ser = Serial("/dev/ttyUSB0", baud_rate, timeout = 0, writeTimeout = 0)
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

def plot_altitude():

    global fig_altitude, dataPlot_altitude, a_altitude

    fig_altitude = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot_altitude = FigureCanvasTkAgg(fig_altitude, master = chart1_frame)
    a_altitude = fig_altitude.add_subplot(111)

    dataPlot_altitude.show()
    dataPlot_altitude.get_tk_widget().pack()

    def plot_cts():
        global a_altitude
        x_axis = range(0, len(data_altitude))

        a_altitude.clear()
        a_altitude.plot(x_axis, data_altitude)

        a_altitude.set_title("Altitude (m)")

        dataPlot_altitude.show()
        dataPlot_altitude.get_tk_widget().pack()

        root.after(1000, plot_cts)

    plot_cts()

def plot_temperature():

    global fig_temp, dataPlot_temp, a_temp

    fig_temp = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot_temp = FigureCanvasTkAgg(fig_temp, master = chart2_frame)
    a_temp = fig_temp.add_subplot(111)

    dataPlot_temp.show()
    dataPlot_temp.get_tk_widget().pack()

    def plot_cts():
        global a_temp
        x_axis = range(0, len(data_temp_outside))

        a_temp.clear()
        a_temp.plot(x_axis, data_temp_outside, "r", label = "Outside")
        a_temp.plot(x_axis, data_temp_inside, "b", label = "Inside")

        a_temp.set_title("Temperature (C)")
        a_temp.set_ylim([-40, 40])
        legend = a_temp.legend(loc='lower right', shadow=True)        

        dataPlot_temp.show()
        dataPlot_temp.get_tk_widget().pack() 

        root.after(1000, plot_cts)

    plot_cts()    

def plot_voltage():

    global fig_voltage, dataPlot_voltage, a_voltage

    fig_voltage = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot_voltage = FigureCanvasTkAgg(fig_voltage, master = chart3_frame)

    a_voltage = fig_voltage.add_subplot(111)
    dataPlot_voltage.show()
    dataPlot_voltage.get_tk_widget().pack()    

    def plot_cts():
        global a_voltage
        a_voltage.clear()

        voltage = data_voltage[len(data_voltage) - 1]
        if voltage > 7.5:
            a_voltage.bar(0, voltage, 1, color = 'g')
        elif voltage > 5.5:
            a_voltage.bar(0, voltage, 1, color = 'y')
        else:
            a_voltage.bar(0, voltage, 1, color = 'r')

        a_voltage.set_title("Voltage (V)")
        a_voltage.set_ylim([0, 10])
        a_voltage.get_xaxis().set_visible(False)            

        dataPlot_voltage.show()
        dataPlot_voltage.get_tk_widget().pack() 

        root.after(1000, plot_cts)

    plot_cts()    

def plot_acc():

    global fig_acc, dataPlot_acc, a_acc

    fig_acc = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16)
    dataPlot_acc = FigureCanvasTkAgg(fig_acc, master = chart4_frame)

    a_acc = fig_acc.add_subplot(111)
    dataPlot_acc.show()
    dataPlot_acc.get_tk_widget().pack()   

    def plot_cts():
        global a_acc
        a_acc.clear()

        a_acc.set_title("Acceleration (x, y, z)")
        a_acc.set_ylim([-500, 500])
        a_acc.get_xaxis().set_visible(False)

        a_acc.bar(0, data_acc_x[len(data_acc_x) - 1], 1, color = 'g')
        a_acc.bar(1, data_acc_y[len(data_acc_y) - 1], 1, color = 'b')
        a_acc.bar(2, data_acc_z[len(data_acc_z) - 1], 1, color = 'r')

        dataPlot_acc.show()
        dataPlot_acc.get_tk_widget().pack()   

        root.after(1000, plot_cts)

    plot_cts()     

def ser_test_write():
    global ser, ser_connected

    if ser_connected:
        data = ser.readline()
        data_list = data.split(",")

        if len(data_list) == 10:
            data_altitude.append(int(data_list[2]))
            data_temp_outside.append(float(data_list[3]))
            data_temp_inside.append(float(data_list[4]))
            data_voltage.append(float(data_list[5]))
            data_state.append(data_list[6])
            data_acc_x.append(float(data_list[7]))
            data_acc_y.append(float(data_list[8]))
            data_acc_z.append(float(data_list[9]))

            listbox.insert(0, data)

    root.after(500, ser_test_write)

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

'''
f = open('../sample_data_file.csv', 'r')
for line in f:
    listbox.insert(0, str(line))
'''

listbox.pack(side = LEFT, fill = BOTH)

scrollbar.config(command=listbox.yview)

# Bottom status bar

root.status = StatusBar(root)
root.status.pack(side='bottom', fill='x')

# Code to run after mainloop

root.after(0, plot_altitude)
root.after(0, plot_temperature)
root.after(0, plot_voltage)
root.after(0, plot_acc)

root.after(1000, ser_test_write)
root.after(1000, conclude)

root.mainloop()