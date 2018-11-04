from tkinter import *
from tkinter.ttk import Combobox
from draw_stats import *

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="Please enter a team name:")
        self.label.pack()

        with open('2018_all_teams.json') as handle:
          teams = json.loads(handle.read())
        
        teams = [team for team in teams]
        teams.sort()

        myVar = StringVar()
        self.team_name = Combobox(master, values=teams, state="readonly")
        self.team_name.pack()

        self.close_button = Button(master, text="Produce Files", command=lambda: main(number_from_name(self.team_name.get())))
        self.close_button.pack()

root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()