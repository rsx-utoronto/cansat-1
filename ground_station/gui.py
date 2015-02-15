import Tkinter as tk
import ttk
import user
import sys
import time

class Root(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        #initialize menu
        self.config(menu=MenuBar(self))

        self.geometry("1000x600+200+50")

        self.appFrame = tk.Frame(self)
        self.appFrame.pack(side='top', fill='both', expand='True')
        
        self.status = StatusBar(self)
        self.status.pack(side='bottom', fill='x')
        
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
        self.add_cascade(label="Telemetry",underline=0, menu=filemenu)
        filemenu.add_command(label="Connect", command=self.callback)
        filemenu.add_command(label="Disconnect", command=self.callback)
        filemenu.add_separator()
        filemenu.add_command(label="USBTTY0", command=self.callback)
        filemenu.add_command(label="USBTTY1", command=self.callback)

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

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

            
class Application(ttk.Notebook):
    def __init__(self, root):
        ttk.Notebook.__init__(self, root)
        
        tab1 = ttk.Frame(self)
        tab2 = ttk.Frame(self)
        
        self.add(tab1, text = "Main GUI")
        self.add(tab2, text = "Raw Data")

def test():
    for i in range(0,10):
        root.status.set(str(i))

root = Root()
root.after(2000, test)
root.mainloop()