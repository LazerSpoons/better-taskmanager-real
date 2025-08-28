from tkinter import *
from tkinter import messagebox, font
from scriptFile import *

# Dummy function from scriptFile, replace with your real import

def killTask():
    newRoot = Toplevel()
    newRoot.title("Kill Task")
    Label(newRoot, text="Enter the name of the task you want to kill", font=default_font).pack(pady=10)
    e = Entry(newRoot, font=default_font)
    e.pack()

    def on_kill_click():
        killProccessByName(e.get())
        newRoot.destroy()

    Button(newRoot, text="Kill Task", font=default_font, command=on_kill_click).pack(pady=10)

def testThing():
    messagebox.showinfo("Hehe", "hehe")

def openFolder():
    messagebox.showinfo("Folder", "Pretend this opened a folder.")

def exitProgram():
    root.quit()

# Create main window
root = Tk()
root.title("Main Window")

# High-DPI scaling for better text rendering
root.tk.call('tk', 'scaling', 2.0)

# Define default font
default_font = ("Segoe UI", 12)

# UI Widgets
Label(root, text="Test Frame", font=default_font).pack(pady=5)
Button(root, text="Test Button", font=default_font, command=root.destroy).pack(pady=5)

lb = Listbox(root, font=default_font)
lb.insert(END, 'Kill Task')
lb.insert(END, 'hehe')
lb.insert(END, 'open folder')
lb.insert(END, 'exit program')
lb.pack(pady=10)

# Dispatch dictionary
actions = {
    "Kill Task": killTask,
    "hehe": testThing,
    "open folder": openFolder,
    "exit program": exitProgram
}

def on_listbox_click(event):
    selection = lb.get(ACTIVE)
    action = actions.get(selection)
    if action:
        action()
    else:
        print(f"No action defined for: {selection}")

lb.bind("<Double-1>", on_listbox_click)

# Run the application
root.mainloop()
