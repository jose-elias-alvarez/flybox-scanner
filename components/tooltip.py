import tkinter as tk


class Tooltip:
    def __init__(self, widget, text="widget info"):
        self.waittime = 500  # miliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)
        self.tw = None

    def onEnter(self, event=None):
        self.schedule = self.widget.after(self.waittime, self.showTip)

    def onLeave(self, event=None):
        self.widget.after_cancel(self.schedule)
        self.hideTip()

    def showTip(self):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tw, text=self.text, wraplength=self.wraplength, background="#ffffff"
        )
        label.pack()

    def hideTip(self):
        if self.tw:
            self.tw.destroy()
