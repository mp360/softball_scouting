from tkinter import Tk, Label, Button, Text
from draw_stats import *

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="Please enter a team number:")
        self.label.pack()

        self.team_number = Text(master)
        self.team_number.pack()

        self.close_button = Button(master, text="Produce Files", command=lambda: main(self.team_number.get('1.0', 'end-1c')))
        self.close_button.pack()

root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()