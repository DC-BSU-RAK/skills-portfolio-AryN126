import tkinter as tk
import random
import math

# -- Some global vars (yeah, I know it's not ideal, but easy to handle for now)
difficulty_level = None
score = 0
question_count = 0
first_try = True
expected_answer = 0
numA = 0
numB = 0
operator = ""

# Color palette – probably tweak this later, kinda soft pastel vibes
BG_COLOR = "#EAF4F4"
BTN_COLOR = "#8ECAE6"
TITLE_COLOR = "#023047"
TEXT_COLOR = "#03506F"


# ------------------ BACKGROUND ANIMATION CLASS ------------------
# adds random mathy shapes floating around. Not super efficient but looks fun.
class FloatingBG(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR, highlightthickness=0)
        self.pack(fill="both", expand=True)
        self.things = []
        self._spawn_shapes()
        self._wiggle()

    def _spawn_shapes(self):
        # some random bright-ish shapes
        colors = ["#8ECAE6", "#FFB703", "#FB8500", "#90EE90", "#A5D8FF", "#FFADAD"]
        math_symbols = ["+", "-", "×", "÷"]
        for _ in range(15):
            x = random.randint(0, 1600)
            y = random.randint(0, 900)
            size = random.randint(40, 120)
            color = random.choice(colors)
            shape = random.choice(["circle", "triangle", "square", "hex", "symbol"])
            dx, dy = random.choice([-2, -1, 1, 2]), random.choice([-2, -1, 1, 2])

            if shape == "symbol":
                obj = self.create_text(
                    x, y, text=random.choice(math_symbols),
                    font=("Arial Rounded MT Bold", random.randint(40, 80)),
                    fill=color
                )
            elif shape == "circle":
                obj = self.create_oval(x, y, x + size, y + size, fill=color, outline="")
            elif shape == "square":
                obj = self.create_rectangle(x, y, x + size, y + size, fill=color, outline="")
            elif shape == "triangle":
                pts = [x, y + size, x + size / 2, y, x + size, y + size]
                obj = self.create_polygon(pts, fill=color, outline="")
            else:  # roughly hexagon – I eyeballed it
                pts = []
                for i in range(6):
                    ang = math.radians(i * 60)
                    px = x + size * math.cos(ang)
                    py = y + size * math.sin(ang)
                    pts.extend([px, py])
                obj = self.create_polygon(pts, fill=color, outline="")

            self.things.append([obj, shape, dx, dy])

    def _wiggle(self):
        for item in self.things:
            obj, shape, dx, dy = item
            self.move(obj, dx, dy)
            coords = self.bbox(obj)
            if not coords:
                continue
            x1, y1, x2, y2 = coords
            # bounce off edges
            if x1 <= 0 or x2 >= self.winfo_width():
                dx = -dx
            if y1 <= 0 or y2 >= self.winfo_height():
                dy = -dy
            item[2], item[3] = dx, dy
        # adjust speed a bit
        self.after(45, self._wiggle)


# ------------------ INTRO + MENU SCREENS ------------------
def clear_screen():
    # yeah, brute-force clear. could refactor later.
    for w in root.winfo_children():
        w.destroy()


def show_intro():
    clear_screen()
    bg = FloatingBG(root)
    frame = tk.Frame(bg, bg=BG_COLOR)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="🧮 MATH QUIZ CHALLENGE 🧠",
             font=("Arial Rounded MT Bold", 36, "bold"), fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=40)

    tk.Label(frame, text="10 quick math problems — test your brain!",
             font=("Arial", 16), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)

    tk.Button(frame, text="Start", width=20, height=2, bg=BTN_COLOR,
              font=("Arial", 14, "bold"), command=show_manual).pack(pady=10)

    tk.Button(frame, text="Exit", width=20, height=2, bg="#FFB703",
              font=("Arial", 14, "bold"), command=root.destroy).pack(pady=10)


def show_manual():
    clear_screen()
    bg = FloatingBG(root)
    frame = tk.Frame(bg, bg=BG_COLOR)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="📘 HOW TO PLAY", font=("Arial Rounded MT Bold", 32, "bold"),
             fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=30)

    rules = (
        "1️⃣ Pick a difficulty (easy, medium, or hard).\n\n"
        "2️⃣ Solve 10 math problems.\n\n"
        "3️⃣ 10 points for first try, 5 if you mess up once.\n\n"
        "4️⃣ Try for that 100/100 perfect run!\n"
    )
    tk.Label(frame, text=rules, font=("Arial", 16), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

    tk.Button(frame, text="Back", width=15, bg="#FB8500", fg="white",
              font=("Arial", 12, "bold"), command=show_intro).pack(pady=10)

    tk.Button(frame, text="Continue", width=15, bg=BTN_COLOR, font=("Arial", 12, "bold"),
              command=show_difficulty).pack(pady=10)


def show_difficulty():
    clear_screen()
    bg = FloatingBG(root)
    frame = tk.Frame(bg, bg=BG_COLOR)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="🎯 CHOOSE DIFFICULTY", font=("Arial Rounded MT Bold", 32, "bold"),
             fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=40)

    tk.Button(frame, text="Easy (1-digit)", width=20, bg=BTN_COLOR, font=("Arial", 12, "bold"),
              command=lambda: start_game(1)).pack(pady=10)

    tk.Button(frame, text="Moderate (2-digit)", width=20, bg="#90EE90", font=("Arial", 12, "bold"),
              command=lambda: start_game(2)).pack(pady=10)

    tk.Button(frame, text="Advanced (4-digit)", width=20, bg="#FFB703", font=("Arial", 12, "bold"),
              command=lambda: start_game(3)).pack(pady=10)

    tk.Button(frame, text="Back", width=15, bg="#FB8500", fg="white",
              font=("Arial", 12, "bold"), command=show_manual).pack(pady=20)


# ------------------ QUIZ LOGIC ------------------
def _rand_num(level):
    if level == 1:
        return random.randint(1, 9)
    elif level == 2:
        return random.randint(10, 99)
    else:
        return random.randint(1000, 9999)


def _pick_operator():
    return random.choice(['+', '-'])


def start_game(level):
    global difficulty_level, score, question_count
    difficulty_level = level
    score = 0
    question_count = 0
    next_q()


def next_q():
    global question_count, first_try, numA, numB, operator, expected_answer
    if question_count >= 10:
        show_results()
        return

    first_try = True
    question_count += 1
    numA = _rand_num(difficulty_level)
    numB = _rand_num(difficulty_level)
    operator = _pick_operator()

    if operator == '-' and numB > numA:  # avoid negatives for now
        numA, numB = numB, numA

    expected_answer = numA + numB if operator == '+' else numA - numB
    show_question(f"{numA} {operator} {numB} = ")


def show_question(qtext):
    clear_screen()
    bg = FloatingBG(root)
    frame = tk.Frame(bg, bg=BG_COLOR)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text=f"Question {question_count}/10",
             font=("Arial", 18, "bold"), fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=15)
    tk.Label(frame, text=qtext, font=("Arial Rounded MT Bold", 42, "bold"),
             fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=30)

    global entry, feedback
    entry = tk.Entry(frame, font=("Arial", 22), width=10, justify="center")
    entry.pack(pady=15)
    entry.focus()

    feedback = tk.Label(frame, text="", font=("Arial Rounded MT Bold", 18),
                        bg=BG_COLOR, fg="#FB8500")
    feedback.pack(pady=10)

    tk.Button(frame, text="Submit", width=12, bg=BTN_COLOR,
              font=("Arial", 12, "bold"), command=check_answer).pack(pady=10)
    tk.Button(frame, text="Quit Quiz", width=12, bg="#FB8500", fg="white",
              font=("Arial", 12, "bold"), command=show_difficulty).pack(pady=5)


def check_answer():
    global score, first_try
    try:
        user_val = int(entry.get())
    except ValueError:
        feedback.config(text="⚠️ Enter a valid number!", fg="red")
        return

    if user_val == expected_answer:
        score += 10 if first_try else 5
        feedback.config(text="✅ Correct! Nice work!", fg="green")
        root.after(1000, next_q)
    else:
        if first_try:
            first_try = False
            feedback.config(text="❌ Nope. Try once more!", fg="red")
        else:
            feedback.config(text=f"❌ Wrong again! Ans: {expected_answer}", fg="red")
            root.after(1500, next_q)


def show_results():
    clear_screen()
    bg = FloatingBG(root)
    frame = tk.Frame(bg, bg=BG_COLOR)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "Needs Work"

    tk.Label(frame, text=f"Final Score: {score}/100",
             font=("Arial Rounded MT Bold", 28, "bold"), fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=30)
    tk.Label(frame, text=f"Grade: {grade}", font=("Arial", 22),
             fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=15)

    tk.Button(frame, text="Play Again", width=18, bg=BTN_COLOR,
              font=("Arial", 12, "bold"), command=show_difficulty).pack(pady=10)
    tk.Button(frame, text="Back to Home", width=18, bg="#FFB703",
              font=("Arial", 12, "bold"), command=show_intro).pack(pady=5)
    tk.Button(frame, text="Exit", width=18, bg="#FB8500", fg="white",
              font=("Arial", 12, "bold"), command=root.destroy).pack(pady=10)


# ------------------ MAIN APP ------------------
root = tk.Tk()
root.title("Math Quiz Game")
root.state('zoomed')
root.configure(bg=BG_COLOR)

show_intro()
root.mainloop()
