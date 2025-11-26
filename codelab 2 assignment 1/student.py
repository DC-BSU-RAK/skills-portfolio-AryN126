from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- Paths based on this file ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "Resources")

DATA_PATH = os.path.join(RESOURCES_DIR, "studentMarks.txt")
BG_PATH = os.path.join(RESOURCES_DIR, "bg.png")   # background image


# ---------- Ensure data file ----------
def ensure_data_file():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            f.write("0\n")


# ---------- Load / Save ----------
def load_students():
    ensure_data_file()
    students = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
        return students
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            continue
        code, name = parts[0], parts[1]
        try:
            c1, c2, c3 = int(parts[2]), int(parts[3]), int(parts[4])
            exam = int(parts[5])
        except:
            continue
        students.append(
            {
                "code": code,
                "name": name,
                "coursework": [c1, c2, c3],
                "exam": exam,
            }
        )
    return students


def save_students(students):
    ensure_data_file()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(str(len(students)) + "\n")
        for s in students:
            f.write(
                f"{s['code']},{s['name']},{s['coursework'][0]},"
                f"{s['coursework'][1]},{s['coursework'][2]},{s['exam']}\n"
            )


# ---------- Calculations ----------
def coursework_total(s):
    return sum(s["coursework"])


def overall_percentage(s):
    total = coursework_total(s) + s["exam"]
    return round((total / 160) * 100, 2)


def student_grade(p):
    if p >= 70:
        return "A"
    if p >= 60:
        return "B"
    if p >= 50:
        return "C"
    if p >= 40:
        return "D"
        # fallthrough
    return "F"


# ---------- Helpers ----------
def center(win, w=800, h=600):
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ---------- Theme ----------
CARD_BG = "#2A0000"
BORDER = "#550000"
PRIMARY = "#FF0000"
PRIMARY_HOVER = "#FF5555"
TEXT = "#F0F0F0"
FOOTER_BG = "#2A0000"
SEARCH_BG = "#330000"

# Fonts
F_HEADER1 = ("Impact", 32, "bold")
F_HEADER2 = ("Arial Black", 28)
F_SUBHEADER = ("Arial Black", 14)
F_LABEL = ("Verdana", 12)
F_ENTRY = ("Arial", 11)
F_BUTTON = ("Helvetica", 10, "bold")
F_TABLE = ("Consolas", 10)


# ---------- Rounded Button ----------
class RoundedButton(tk.Canvas):
    def __init__(
        self,
        master,
        text,
        command=None,
        width=120,
        height=36,
        radius=12,
        bg=PRIMARY,
        fg="white",
        hover=PRIMARY_HOVER,
        font=F_BUTTON,
        **kw,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bg=master["bg"],
            **kw,
        )
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover = hover
        self.radius = radius
        self.font = font
        self.text = text

        self._draw()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self._draw(self.hover))
        self.bind("<Leave>", lambda e: self._draw())

    def _draw(self, color=None):
        self.delete("all")
        c = color or self.bg
        w = int(self["width"])
        h = int(self["height"])
        r = self.radius

        self.create_arc((0, 0, r * 2, r * 2), start=90, extent=90, fill=c, outline=c)
        self.create_arc((w - 2 * r, 0, w, h), start=0, extent=90, fill=c, outline=c)
        self.create_arc(
            (0, h - 2 * r, r * 2, h), start=180, extent=90, fill=c, outline=c
        )
        self.create_arc(
            (w - 2 * r, h - 2 * r, w, h),
            start=270,
            extent=90,
            fill=c,
            outline=c,
        )
        self.create_rectangle((r, 0, w - r, h), fill=c, outline=c)
        self.create_rectangle((0, r, w, h - r), fill=c, outline=c)
        self.create_text(w // 2, h // 2, text=self.text, fill=self.fg, font=self.font)

    def _on_click(self, event):
        if self.command:
            self.command()


# ---------- Popup ----------
class PopupCard(tk.Toplevel):
    def __init__(self, parent, title, width=400, height=300):
        super().__init__(parent)
        self.title(title)
        center(self, width, height)

        # Full theme match (red + black)
        self.configure(bg="#1A0000")  # deep blackish-red background
        self.resizable(False, False)
        self.result = None

        # Card Frame
        card = tk.Frame(
            self,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=3
        )
        card.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        tk.Label(
            card,
            text=title,
            bg=CARD_BG,
            fg="#FF5555",
            font=("Arial Black", 16, "bold")
        ).pack(pady=(5, 10))

        # Inner content frame
        self.content_frame = tk.Frame(card, bg=CARD_BG)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.card = card

    def add_close(self):
        btn = RoundedButton(self.card, "Close", command=self.destroy, width=120, height=36)
        btn.pack(pady=10)


# ---------- Main App ----------
class StudentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager — Red-Black GUI")
        center(self.root, 980, 600)
        self.root.configure(bg="black")  # covered by bg image

        # ----- Dynamic Fullscreen Background Image -----
        self.original_bg = Image.open(BG_PATH)

        self.bg_label = tk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        def _resize_bg(event):
            # ignore weird tiny events
            if event.width <= 0 or event.height <= 0:
                return
            resized = self.original_bg.resize((event.width, event.height))
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg_photo)

        # Bind window resize to background redraw
        self.root.bind("<Configure>", _resize_bg)

        # Force one initial draw
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w > 0 and h > 0:
            resized = self.original_bg.resize((w, h))
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg_photo)

        # Use root grid directly
        self.root.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Table style
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT,
            rowheight=28,
            font=F_TABLE,
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=BORDER,
            foreground=TEXT,
            font=F_SUBHEADER,
        )

        self.students = load_students()
        self.sort_asc = True

        self.build_heading()
        self.build_dashboard()
        self.build_ui()
        self.refresh_summary()

    # ---------- Heading ----------
    def build_heading(self):
        heading_frame = tk.Frame(self.root, bg=self.root["bg"])
        heading_frame.grid(row=0, column=0, pady=(10, 5))

        tk.Label(
            heading_frame,
            text="STUDENT",
            font=F_HEADER1,
            fg="#FF5555",
            bg=self.root["bg"]
        ).pack(side="left")

        tk.Label(
            heading_frame,
            text="MANAGEMENT",
            font=F_HEADER2,
            fg="#00FFFF",
            bg=self.root["bg"]
        ).pack(side="left", padx=10)

    # ---------- Dashboard ----------
    def build_dashboard(self):
        dash_frame = tk.Frame(
            self.root,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        dash_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 5))
        dash_frame.columnconfigure(0, weight=1)

        self.total_label = tk.Label(
            dash_frame, text="Total Students: 0", bg=CARD_BG, fg=TEXT, font=F_LABEL
        )
        self.avg_label = tk.Label(
            dash_frame, text="Average Overall %: 0", bg=CARD_BG, fg=TEXT, font=F_LABEL
        )
        self.total_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.avg_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.grade_canvas = tk.Canvas(
            dash_frame, width=300, height=80, bg=CARD_BG, highlightthickness=0
        )
        self.grade_canvas.grid(row=0, column=1, rowspan=2, padx=10)

    # ---------- Dashboard refresh ----------
    def refresh_dashboard(self):
        total = len(self.students)
        if total == 0:
            avg = 0
        else:
            avg = round(
                sum(overall_percentage(s) for s in self.students) / total,
                2,
            )
        self.total_label.config(text=f"Total Students: {total}")
        self.avg_label.config(text=f"Average Overall %: {avg}%")

        grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for s in self.students:
            g = student_grade(overall_percentage(s))
            grades[g] += 1
        self.grade_canvas.delete("all")
        if total == 0:
            return
        x0, y0, r = 150, 40, 30
        start = 0
        colors = {
            "A": "#00FF00",
            "B": "#88FF00",
            "C": "#FFFF00",
            "D": "#FF8800",
            "F": "#FF0000",
        }
        for g in ["A", "B", "C", "D", "F"]:
            extent = (grades[g] / total) * 360
            self.grade_canvas.create_arc(
                x0 - r,
                y0 - r,
                x0 + r,
                y0 + r,
                start=start,
                extent=extent,
                fill=colors[g],
                outline="",
            )
            start += extent
        lx = 10
        for g in ["A", "B", "C", "D", "F"]:
            self.grade_canvas.create_rectangle(lx, 70, lx + 10, 80, fill=colors[g])
            self.grade_canvas.create_text(
                lx + 20,
                75,
                text=f"{g}:{grades[g]}",
                fill=TEXT,
                anchor="w",
                font=("Verdana", 9),
            )
            lx += 50

    # ---------- UI ----------
    def build_ui(self):
        # Search
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_summary())
        search = tk.Frame(self.root, bg=self.root["bg"])
        search.grid(row=2, column=0, sticky="w", padx=20)
        tk.Label(
            search,
            text="Search (name/code):",
            fg=TEXT,
            bg=self.root["bg"],
            font=F_LABEL,
        ).pack(side="left")
        e = tk.Entry(
            search,
            textvariable=self.search_var,
            bg=SEARCH_BG,
            fg=TEXT,
            font=F_ENTRY,
            relief="flat",
            width=40,
            highlightthickness=2,
            highlightbackground=BORDER,
            highlightcolor=PRIMARY,
        )
        e.pack(side="left", padx=8, ipady=6)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=self.root["bg"])
        btn_frame.grid(row=3, column=0, pady=10)
        buttons = [
            ("View All", self.open_all_popup),
            ("View Individual", self.view_individual),
            ("Highest Score", self.show_top),
            ("Lowest Score", self.show_low),
            ("Sort (A⇅D)", self.toggle_sort),
            ("Add", self.add_student),
            ("Delete", self.delete_student),
            ("Update", self.update_student),
            ("Refresh", self.refresh_data),
        ]
        for txt, cmd in buttons:
            btn = RoundedButton(btn_frame, text=txt, command=cmd, width=130, height=36)
            btn.pack(side="left", padx=6, pady=4)

        # Table
        table_card = tk.Frame(
            self.root,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        table_card.grid(row=4, column=0, sticky="nsew", padx=20)
        self.root.rowconfigure(4, weight=1)
        table_card.rowconfigure(0, weight=1)
        table_card.columnconfigure(0, weight=1)

        cols = ("code", "name", "cw_total", "exam", "overall", "grade")
        self.tv = ttk.Treeview(
            table_card, columns=cols, show="headings", style="Custom.Treeview"
        )
        setup = [
            ("code", "Code", 100, "center"),
            ("name", "Name", 350, "w"),
            ("cw_total", "CW Total", 120, "center"),
            ("exam", "Exam", 100, "center"),
            ("overall", "Overall %", 100, "center"),
            ("grade", "Grade", 80, "center"),
        ]
        for c, t, w, a in setup:
            self.tv.heading(c, text=t, anchor=a)
            self.tv.column(c, width=w, anchor=a)
        vsb = ttk.Scrollbar(table_card, command=self.tv.yview)
        self.tv.configure(yscrollcommand=vsb.set)
        self.tv.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.footer = tk.Label(
            self.root,
            text="",
            fg=TEXT,
            bg=FOOTER_BG,
            font=F_LABEL,
        )
        self.footer.grid(row=5, column=0, sticky="ew")

    # ---------- Refresh summary ----------
    def refresh_summary(self):
        self.students = load_students()
        q = self.search_var.get().lower().strip()
        self.tv.delete(*self.tv.get_children())
        for s in self.students:
            pct = overall_percentage(s)
            if q and q not in s["name"].lower() and q not in s["code"]:
                continue
            self.tv.insert(
                "",
                "end",
                iid=s["code"],
                values=(
                    s["code"],
                    s["name"],
                    coursework_total(s),
                    s["exam"],
                    f"{pct}%",
                    student_grade(pct),
                ),
            )
        self.refresh_dashboard()
        avg = (
            round(
                sum(overall_percentage(s) for s in self.students)
                / len(self.students),
                2,
            )
            if self.students
            else 0
        )
        self.footer.config(
            text=f"Total Students: {len(self.students)}    Average Overall %: {avg}%"
        )

    # ---------- Core Actions ----------
    def view_individual(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("Select Student", "Please select a student.")
            return
        self.show_student(sel[0])

    def show_top(self):
        if not self.students:
            return
        s = max(self.students, key=lambda x: overall_percentage(x))
        self.show_student(s["code"])

    def show_low(self):
        if not self.students:
            return
        s = min(self.students, key=lambda x: overall_percentage(x))
        self.show_student(s["code"])

    def toggle_sort(self):
        self.students.sort(
            key=lambda x: overall_percentage(x),
            reverse=self.sort_asc,
        )
        self.sort_asc = not self.sort_asc
        save_students(self.students)
        self.refresh_summary()

    # ---------- Popups ----------
    def show_student(self, code):
        s = next((x for x in self.students if x["code"] == code), None)
        if not s:
            return
        p = PopupCard(self.root, f"{s['name']} ({s['code']})", 400, 300)
        tk.Label(
            p.content_frame,
            text=(
                f"Code: {s['code']}\n"
                f"Name: {s['name']}\n"
                f"CW Total: {coursework_total(s)}\n"
                f"Exam: {s['exam']}\n"
                f"Overall %: {overall_percentage(s)}\n"
                f"Grade: {student_grade(overall_percentage(s))}"
            ),
            bg=CARD_BG,
            fg=TEXT,
            justify="left",
            font=F_ENTRY,
        ).pack(pady=20)
        p.add_close()
        p.grab_set()
        p.wait_window()

    def input_popup(self, title, fields):
        p = PopupCard(self.root, title, 420, 330)
        entries = {}
        for lbl, value in fields.items():
            row = tk.Frame(p.content_frame, bg=CARD_BG)
            row.pack(fill="x", pady=5)
            tk.Label(
                row,
                text=lbl + ":",
                fg=TEXT,
                bg=CARD_BG,
                font=F_LABEL,
            ).pack(side="left")
            var = tk.StringVar(value=value)
            e = tk.Entry(
                row,
                textvariable=var,
                bg=SEARCH_BG,
                fg=TEXT,
                font=F_ENTRY,
                relief="flat",
                width=25,
                highlightthickness=2,
                highlightbackground=BORDER,
                highlightcolor=PRIMARY,
            )
            e.pack(side="left", padx=10)
            entries[lbl] = var

        def submit():
            p.result = {k: v.get() for k, v in entries.items()}
            p.destroy()

        btn = RoundedButton(p.card, "Submit", command=submit)
        btn.pack(pady=8)
        p.grab_set()
        p.wait_window()
        return p.result

    # ---------- Add / Update / Delete / Refresh ----------
    def add_student(self):
        res = self.input_popup(
            "Add Student",
            {"Code": "", "Name": "", "CW1": "0", "CW2": "0", "CW3": "0", "Exam": "0"},
        )
        if not res:
            return
        try:
            code = res["Code"].strip()
            name = res["Name"].strip()
            cw = [int(res["CW1"]), int(res["CW2"]), int(res["CW3"])]
            exam = int(res["Exam"])
            if not (0 <= exam <= 100 and all(0 <= c <= 20 for c in cw)):
                raise ValueError
        except Exception:
            messagebox.showwarning(
                "Invalid Input", "Enter valid CW (0–20) and Exam (0–100)."
            )
            return
        if any(s["code"] == code for s in self.students):
            messagebox.showwarning("Duplicate Code", "Student code already exists.")
            return
        self.students.append(
            {"code": code, "name": name, "coursework": cw, "exam": exam}
        )
        save_students(self.students)
        self.refresh_summary()

    def update_student(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("Select Student", "Select student to update.")
            return
        s = next((x for x in self.students if x["code"] == sel[0]), None)
        res = self.input_popup(
            "Update Student",
            {
                "Code": s["code"],
                "Name": s["name"],
                "CW1": s["coursework"][0],
                "CW2": s["coursework"][1],
                "CW3": s["coursework"][2],
                "Exam": s["exam"],
            },
        )
        if not res:
            return
        try:
            cw = [int(res["CW1"]), int(res["CW2"]), int(res["CW3"])]
            exam = int(res["Exam"])
            if not (0 <= exam <= 100 and all(0 <= c <= 20 for c in cw)):
                raise ValueError
        except Exception:
            messagebox.showwarning(
                "Invalid Input", "Enter valid CW (0–20) and Exam (0–100)."
            )
            return
        s.update({"name": res["Name"], "coursework": cw, "exam": exam})
        save_students(self.students)
        self.refresh_summary()

    def delete_student(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("Select Student", "Select student to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete selected student?"):
            self.students = [s for s in self.students if s["code"] != sel[0]]
            save_students(self.students)
            self.refresh_summary()

    def refresh_data(self):
        self.refresh_summary()

    # ---------- View All ----------
    def open_all_popup(self):
        p = PopupCard(self.root, "All Students", 600, 400)
        tv = ttk.Treeview(
            p.content_frame,
            columns=("code", "name", "cw", "exam", "overall", "grade"),
            show="headings",
        )
        for c, h in [
            ("code", "Code"),
            ("name", "Name"),
            ("cw", "CW Total"),
            ("exam", "Exam"),
            ("overall", "Overall %"),
            ("grade", "Grade"),
        ]:
            tv.heading(c, text=h)
            tv.column(c, width=100, anchor="center")
        for s in self.students:
            tv.insert(
                "",
                "end",
                values=(
                    s["code"],
                    s["name"],
                    coursework_total(s),
                    s["exam"],
                    overall_percentage(s),
                    student_grade(overall_percentage(s)),
                ),
            )
        tv.pack(expand=True, fill="both")
        p.add_close()
        p.grab_set()
        p.wait_window()


# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagerApp(root)
    root.mainloop()
