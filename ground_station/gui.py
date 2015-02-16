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
import ttk, user, sys, time, serial, datetime
from subprocess import check_output
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

root = tk.Tk()

def key(event):
    root.status.set(repr(event.char)) 

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        filemenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File",underline=0, menu=filemenu)
        filemenu.add_command(label="Start", command=self.callback)
        filemenu.add_command(label="Pause", command=self.callback)
        filemenu.add_command(label="Stop", command=self.callback)
        filemenu.add_separator()                
        filemenu.add_command(label="Exit", underline=1, command=self.quit)

        filemenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Establish Connection",underline=0, menu=filemenu)

        found_port = False
        for port in check_output(["ls", "/dev"]).split("\n"):
            if port.find("USB") != -1:
                found_port = True
                filemenu.add_command(label=port, command=self.callback)

        filemenu.add_separator()
        filemenu.add_command(label="Disconnect", command=self.callback)

        if not found_port:
            filemenu.add_command(label="No COM Device Found")

        helpmenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.callback)

    def quit(self):
        sys.exit(0)
    
    def callback(self):
        print "called the callback!"

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

    f = Figure(figsize=(4, 4), dpi = (frame.winfo_width() - 50) / 16, facecolor = "white")
    dataPlot = FigureCanvasTkAgg(f, master = location)
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    a = f.add_subplot(111)
    a.plot(data)

    a.set_title("Random Data")
    f.set_frameon(False)
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

def conclude():
    frame.focus_set()

root.config(menu=MenuBar(root))
root.geometry("1000x600+200+50")
root.title("RSX CanSat Control Center Version 1.0")
#root.configure(background='white')

top_info_frame = Frame(root)
top_info_frame.pack(side = "top", pady = 20, fill = X)

label_top1 = Label(top_info_frame, text = "TEAM #1171")
label_top1.pack(side=LEFT, expand = 1, fill = X)
label_top2 = Label(top_info_frame, text = "Mission Time: %s" % str(datetime.datetime.now()))
label_top2.pack(side=LEFT, expand = 1, fill = X)
label_top2 = Label(top_info_frame, text = "Flight Status: Ascending")
label_top2.pack(side=LEFT, expand = 1, fill = X)

frame = Frame(root, padx = 10, pady = 10)
frame.pack(side='top', fill='both', expand='True')
frame.bind("<Key>", key)
frame.focus_set()

root.status = StatusBar(root)
root.status.pack(side='bottom', fill='x')

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

root.after(0, plot_altitude(chart1_frame))
root.after(0, plot_altitude(chart2_frame))
root.after(0, plot_altitude(chart3_frame))
root.after(0, plot_altitude(chart4_frame))

root.after(1000, conclude)

root.mainloop()