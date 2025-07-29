import os
import sys
import asyncio
import threading
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image # for PVRTexLibPy

# dont import btx cause you need only python 3.9 :3
try:
    import PVRTexLibPy as pvrpy
    CAN_BTX = True
except ImportError:
    CAN_BTX = False

from bpc import convert_bpc_file
from cls import split_cls_file
import mod

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

icon_path = os.path.join(base_path, "icon.ico")
app.iconbitmap(icon_path)

app.title("unware")
app.geometry("700x400")

tabview = ctk.CTkTabview(app, width=660, height=100)
for name in ["BPC", "CLS", "MOD", "BTX"]:
    tabview.add(name)
tabview.pack(padx=20, pady=20)

log_box = ctk.CTkTextbox(app, height=200, state="disabled")
log_box.pack(fill="both", expand=False, padx=20, pady=(0,20))

def log(msg):
    app.after(0, lambda: _append_log(msg))

def _append_log(msg):
    log_box.configure(state="normal")
    log_box.insert("end", msg + "\n")
    log_box.see("end")
    log_box.configure(state="disabled")

def select_file(entry, ft):
    p = filedialog.askopenfilename(filetypes=ft)
    if p:
        entry.delete(0, "end")
        entry.insert(0, p)

def select_files(entry, ft):
    ps = filedialog.askopenfilenames(filetypes=ft)
    if ps:
        entry.delete(0, "end")
        entry.insert(0, ";".join(ps))

def select_dir(entry):
    d = filedialog.askdirectory()
    if d:
        entry.delete(0, "end")
        entry.insert(0, d)

def _run_in_thread(func, *args):
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()

def run_bpc(inp, out):
    def task():
        if not inp:
            log("select .bpc file")
            return
        try:
            res = convert_bpc_file(inp, out or None)
            log(f"[✓] BPC → {res}")
        except Exception as e:
            log(f"[X] BPC error: {e}")
    _run_in_thread(task)

# TODO async
def run_cls(files, out):
    def task():
        if not files:
            log("select .cls files")
            return
        success = False
        for f in files:
            try:
                parts = split_cls_file(f, out or 'col')
                for p in parts:
                    log(f"[~] CLS → {p}")
                success = True
            except Exception as e:
                log(f"[X] CLS error: {e}")
        if success:
            log("[✓] CLS done")
    _run_in_thread(task)

def run_mod(files, out):
    def task():
        if not files:
            log("select .mod files")
            return
        try:
            mod.convert(files, out or '.', log)
            log("[✓] MOD done")
        except Exception as e:
            log(f"[X] MOD error: {e}")
    _run_in_thread(task)

def run_btx(files, out):
    def task():
        if not CAN_BTX:
            log("[!] BTX unavailable")
            return
        try:
            import btx
            btx.convert(files, out or 'png', log=log)
            log("[✓] BTX done")
        except Exception as e:
            log(f"[X] BTX error: {e}")
    _run_in_thread(task)

def setup_bpc_tab():
    f = tabview.tab("BPC")
    ctk.CTkLabel(f, text="input .bpc:").grid(row=0, column=0, sticky="w", pady=5)
    e_in = ctk.CTkEntry(f, width=400)
    e_in.grid(row=0, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_file(e_in, [("BPC","*.bpc")])).grid(row=0, column=2)

    ctk.CTkLabel(f, text="output folder:").grid(row=1, column=0, sticky="w", pady=5)
    e_out = ctk.CTkEntry(f, width=400)
    e_out.grid(row=1, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_dir(e_out)).grid(row=1, column=2)

    ctk.CTkButton(f, text="decrypt BPC",
                  command=lambda: run_bpc(e_in.get(), e_out.get())).grid(row=2, column=0, columnspan=3, pady=10)

def setup_cls_tab():
    f = tabview.tab("CLS")
    ctk.CTkLabel(f, text="input .cls:").grid(row=0, column=0, sticky="w", pady=5)
    e_in = ctk.CTkEntry(f, width=400)
    e_in.grid(row=0, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_files(e_in, [("CLS","*.cls")])).grid(row=0, column=2)

    ctk.CTkLabel(f, text="output folder:").grid(row=1, column=0, sticky="w", pady=5)
    e_out = ctk.CTkEntry(f, width=400)
    e_out.grid(row=1, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_dir(e_out)).grid(row=1, column=2)

    ctk.CTkButton(f, text="decrypt CLS",
                  command=lambda: run_cls(e_in.get().split(';'), e_out.get())).grid(row=2, column=0, columnspan=3, pady=10)

def setup_mod_tab():
    f = tabview.tab("MOD")
    ctk.CTkLabel(f, text="input .mod:").grid(row=0, column=0, sticky="w", pady=5)
    e_in = ctk.CTkEntry(f, width=400)
    e_in.grid(row=0, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_files(e_in, [("MOD","*.mod")])).grid(row=0, column=2)

    ctk.CTkLabel(f, text="output folder:").grid(row=1, column=0, sticky="w", pady=5)
    e_out = ctk.CTkEntry(f, width=400)
    e_out.grid(row=1, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_dir(e_out)).grid(row=1, column=2)

    ctk.CTkButton(f, text="decrypt MOD",
                  command=lambda: run_mod(e_in.get().split(';'), e_out.get())).grid(row=2, column=0, columnspan=3, pady=10)

def setup_btx_tab():
    f = tabview.tab("BTX")
    ctk.CTkLabel(f, text="input .btx:").grid(row=0, column=0, sticky="w", pady=5)
    e_in = ctk.CTkEntry(f, width=400)
    e_in.grid(row=0, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_files(e_in, [("BTX","*.btx")])).grid(row=0, column=2)

    ctk.CTkLabel(f, text="output folder:").grid(row=1, column=0, sticky="w", pady=5)
    e_out = ctk.CTkEntry(f, width=400)
    e_out.grid(row=1, column=1, pady=5, padx=5)
    ctk.CTkButton(f, text="browse", command=lambda: select_dir(e_out)).grid(row=1, column=2)

    state = "normal" if CAN_BTX else "disabled"
    ctk.CTkButton(f, text="decrypt BTX", state=state,
                  command=lambda: run_btx(e_in.get().split(';'), e_out.get())).grid(row=2, column=0, columnspan=3, pady=10)

setup_bpc_tab()
setup_cls_tab()
setup_mod_tab()
setup_btx_tab()

app.mainloop()
