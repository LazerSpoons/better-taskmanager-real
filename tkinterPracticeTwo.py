import tkinter as tk
from tkinter import ttk, messagebox
import scriptFile as sf
import sv_ttk as svtk
import pywinstyles, sys

# --- Helpers ---
def apply_theme_to_titlebar(win):
    version = sys.getwindowsversion()
    if version.major == 10 and version.build >= 22000:
        pywinstyles.change_header_color(win, "#1c1c1c" if svtk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(win, "dark" if svtk.get_theme() == "dark" else "normal")

# --- Actions ---
def killTask():
    win = tk.Toplevel(root)
    win.title("Kill Task")

    ttk.Label(win, text="Enter exact process name (without .exe):").grid(row=0, column=0, padx=10, pady=(10, 4), sticky="w")
    e = ttk.Entry(win)
    e.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")

    def on_kill():
        name = e.get().strip()
        if not name:
            messagebox.showwarning("Missing", "Please enter a process name.")
            return
        if sf.killProccessByName(name):
            messagebox.showinfo("Done", f"Killed '{name}.exe'")
        else:
            messagebox.showwarning("Not found", f"No running process named '{name}.exe'")
        win.destroy()

    ttk.Button(win, text="Kill", command=on_kill).grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
    e.focus_set()

    win.columnconfigure(0, weight=1)
    apply_theme_to_titlebar(win)

def searchAndDestroy():
    win = tk.Toplevel(root)
    win.title("Search & Destroy")
    win.geometry("420x420")

    # Internal state to map listbox rows -> (pid, name)
    results = []

    # Query row
    ttk.Label(win, text="Enter part of the process name:").grid(row=0, column=0, padx=10, pady=(10, 4), sticky="w")
    q = ttk.Entry(win)
    q.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")

    # Listbox + scrollbar
    ttk.Label(win, text="Matching items:").grid(row=2, column=0, padx=10, sticky="w")
    list_frame = ttk.Frame(win)
    list_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
   

    lst = tk.Listbox(list_frame, height=14, selectmode=tk.EXTENDED)  # allow multi-select
    vsb = ttk.Scrollbar(list_frame, orient="vertical", command=lst.yview)
    lst.configure(yscrollcommand=vsb.set)

    lst.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)

    # Actions
    def do_search(*_):
        nonlocal results
        lst.delete(0, tk.END)
        query = q.get().strip()
        results = sf.search(query) or []  # Expecting iterable of (pid, name) or similar
        for (pid, name) in results:
            lst.insert(tk.END, f"{pid}\t{name}")

    def do_kill_selected():
        sel_indices = lst.curselection()
        if not sel_indices:
            messagebox.showwarning("No selection", "Please select one or more items to kill.")
            return

        # Gather selected PIDs and names
        to_kill = []
        for idx in sel_indices:
            try:
                pid, name = results[idx][0], results[idx][1]
                to_kill.append((int(pid), name))
            except Exception:
                # Skip bad rows defensively
                continue

        if not to_kill:
            messagebox.showwarning("No valid selection", "Could not parse selected items.")
            return

        # Optional confirm
        names_preview = ", ".join(f"{pid}({name})" for pid, name in to_kill[:8])
        if len(to_kill) > 8:
            names_preview += ", ..."
        if not messagebox.askyesno("Confirm kill",
                                   f"Kill {len(to_kill)} process(es)?\n{names_preview}"):
            return

        successes, failures = 0, 0
        failed_items = []
        for pid, name in to_kill:
            try:
                if sf.kill_by_pid(pid):
                    successes += 1
                else:
                    failures += 1
                    failed_items.append(f"{pid}({name})")
            except Exception:
                failures += 1
                failed_items.append(f"{pid}({name})")

        # Refresh list after action
        do_search()

        if failures == 0:
            messagebox.showinfo("Done", f"Killed {successes} process(es).")
        else:
            messagebox.showwarning(
                "Partial",
                f"Killed {successes} process(es).\nFailed: {failures}\n{', '.join(failed_items[:10])}"
            )

    # Bottom buttons row
    btn_frame = ttk.Frame(win)
    btn_frame.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

    ttk.Button(btn_frame, text="Search", command=do_search).grid(row=0, column=0, padx=5, sticky="ew")
    ttk.Button(btn_frame, text="Kill Selected", command=do_kill_selected).grid(row=0, column=1, padx=5, sticky="ew")

    # Stretch columns
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)
    win.columnconfigure(0, weight=1)
    win.rowconfigure(3, weight=1)

    # Nice-to-have: Enter triggers search, Ctrl+A selects all
    q.bind("<Return>", do_search)
    win.bind("<Control-a>", lambda e: (lst.select_set(0, tk.END), "break"))
    q.focus_set()

    apply_theme_to_titlebar(win)

# --- Main Window ---
root = tk.Tk()
root.title("Main Window")
root.geometry("300x200")

svtk.use_dark_theme()

ttk.Label(root, text="Select an action:", font=("Arial", 14)).grid(row=0, column=0, pady=10, padx=10)
ttk.Button(root, text="Close Program (Kill by name)", command=killTask).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
ttk.Button(root, text="Search & Destroy", command=searchAndDestroy).grid(row=2, column=0, padx=10, pady=5, sticky="ew")

root.columnconfigure(0, weight=1)

apply_theme_to_titlebar(root)
root.mainloop()
