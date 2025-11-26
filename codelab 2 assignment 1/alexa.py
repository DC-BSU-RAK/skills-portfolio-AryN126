import tkinter as tk
import random
import os
from PIL import Image, ImageTk, ImageSequence

# =====================
#  PATH HELPERS
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RES_DIR = os.path.join(BASE_DIR, "Resources")


def res_path(name: str) -> str:
    return os.path.join(RES_DIR, name)


# =====================
#  OPTIONAL: SOUND FX
# =====================
try:
    import pygame
    pygame.mixer.init()
    USE_SOUND = True
except Exception:
    pygame = None
    USE_SOUND = False


def load_sound(path):
    if not USE_SOUND:
        return None
    try:
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    except Exception:
        pass
    return None


def play_sound(sound):
    if sound is not None and USE_SOUND:
        try:
            sound.play()
        except Exception:
            pass


# --- Sound file paths (match your Resources folder) ---
SFX_PUNCHLINE = res_path("laugh-105488.mp3")   # laugh
SFX_NEW_JOKE = res_path("bah-dum-tss-47996.mp3")    # rimshot 

sfx_punchline = load_sound(SFX_PUNCHLINE)
sfx_new_joke = load_sound(SFX_NEW_JOKE)


# =====================
#  LOAD JOKES
# =====================
jokes = []
jokes_file = res_path("randomJokes.txt")

try:
    with open(jokes_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if "?" in line:
                setup, punchline = line.split("?", 1)
                jokes.append((setup.strip() + "?", punchline.strip()))
except FileNotFoundError:
    jokes = [("Jokes file not found?", "Make sure randomJokes.txt is in the Resources folder!")]

current_joke = ("", "")


# =====================
#  FONTS (UPDATED)
# =====================
FONT_MAIN = ("Arial Rounded MT Bold", 26, "bold")   # setup panel
FONT_SUB = ("Arial", 16)                            # small texts
STATUS_FONT = ("Arial", 16, "italic")               # "thinking..." line
PUNCH_BASE_SIZE = 20
PUNCH_FONT = ("Arial", PUNCH_BASE_SIZE, "bold")     # punchline
BUTTON_FONT = ("Arial", 15, "bold")                 # main buttons


# =====================
#  ROOT & CANVAS
# =====================
root = tk.Tk()
root.title("Alexa Joke Assistant (Comic Edition)")

# Fullscreen
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

canvas = tk.Canvas(root, width=screen_w, height=screen_h,
                   highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)


# =====================
#  IMAGE LOADER
# =====================
def load_image(path, size=None):
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path)
        if size is not None:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


# =====================
#  ANIMATED GIF BACKGROUND
# =====================
bg_frames = []
bg_frame_index = 0
bg_canvas_item = None


def animate_background():
    """Loop through GIF frames on the canvas."""
    global bg_frame_index
    if not bg_frames or bg_canvas_item is None:
        return

    bg_frame_index = (bg_frame_index + 1) % len(bg_frames)
    canvas.itemconfig(bg_canvas_item, image=bg_frames[bg_frame_index])
    # Adjust speed here
    root.after(80, animate_background)


def set_animated_background(gif_path):
    """Load GIF, resize to fullscreen and animate as background."""
    global bg_frames, bg_frame_index, bg_canvas_item

    if not os.path.exists(gif_path):
        # Fallback solid color
        canvas.configure(bg="#1e1b4b")
        return

    try:
        gif = Image.open(gif_path)
    except Exception:
        canvas.configure(bg="#1e1b4b")
        return

    bg_frames = []
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        frame = frame.resize((screen_w, screen_h))
        bg_frames.append(ImageTk.PhotoImage(frame))

    if not bg_frames:
        canvas.configure(bg="#1e1b4b")
        return

    bg_frame_index = 0
    # Create background image item ONCE (bottom layer)
    bg_canvas_item = canvas.create_image(0, 0, image=bg_frames[0], anchor="nw")
    animate_background()


# Use your GIF as background (VERY IMPORTANT: before any other draws)
set_animated_background(res_path("joke.gif"))


# =====================
#  COMIC BORDER
# =====================
canvas.create_rectangle(
    10, 10, screen_w - 10, screen_h - 10,
    outline="black", width=8
)

center_x = screen_w // 2


# =====================
#  COMIC PANELS
# =====================
panel_width = int(screen_w * 0.7)
panel_height = int(screen_h * 0.15)

# Setup narration panel
setup_y_top = int(screen_h * 0.10)

setup_x1 = center_x - panel_width // 2
setup_y1 = setup_y_top
setup_x2 = center_x + panel_width // 2
setup_y2 = setup_y1 + panel_height

canvas.create_rectangle(
    setup_x1, setup_y1, setup_x2, setup_y2,
    fill="#A78BFA",    # soft violet
    outline="black",
    width=5
)

setup_text_id = canvas.create_text(
    center_x,
    setup_y1 + panel_height // 2,
    text="Click 'Alexa tell me a Joke' to start!",
    font=FONT_MAIN,
    fill="black",
    width=int(panel_width * 0.9),
    justify="center"
)

# Punchline speech bubble
punch_y_top = int(screen_h * 0.30)

punch_x1 = setup_x1 + 30
punch_y1 = punch_y_top
punch_x2 = setup_x2 - 30
punch_y2 = punch_y1 + panel_height

canvas.create_rectangle(
    punch_x1, punch_y1, punch_x2, punch_y2,
    fill="#FFFFFF",
    outline="#4C1D95",   # deep purple outline
    width=6
)

# Bubble tail
tail_x = center_x
tail_y1 = punch_y2
tail_y2 = punch_y2 + 35

canvas.create_polygon(
    tail_x - 30, tail_y1,
    tail_x + 30, tail_y1,
    tail_x, tail_y2,
    fill="#FFFFFF",
    outline="#4C1D95",
    width=3
)

punchline_text_id = canvas.create_text(
    center_x,
    punch_y1 + panel_height // 2,
    text="",
    font=PUNCH_FONT,
    fill="#1A1A1A",   # dark grey for punchline
    width=int((punch_x2 - punch_x1) * 0.9),
    justify="center"
)

# Status text (for "Alexa is thinking..." etc.)
status_text_id = canvas.create_text(
    center_x,
    int(screen_h * 0.47),
    text="",
    font=STATUS_FONT,
    fill="#4ade80",   # fresh green
    width=int(panel_width * 0.7),
    justify="center"
)

base_punch_coords = canvas.coords(punchline_text_id)


# =====================
#  ANIMATIONS
# =====================
def animate_punch_pop(step=0):
    sizes = [PUNCH_BASE_SIZE + 8, PUNCH_BASE_SIZE + 4, PUNCH_BASE_SIZE]
    if step < len(sizes):
        canvas.itemconfig(
            punchline_text_id,
            font=("Arial", sizes[step], "bold")
        )
        root.after(80, animate_punch_pop, step + 1)


def animate_punch_shake(step=0):
    global base_punch_coords
    if step == 0:
        base_punch_coords = canvas.coords(punchline_text_id)

    if step < 6:
        dx = 6 if step % 2 == 0 else -6
        canvas.move(punchline_text_id, dx, 0)
        root.after(40, animate_punch_shake, step + 1)
    else:
        if base_punch_coords:
            canvas.coords(punchline_text_id, *base_punch_coords)


def show_punchline_after_thinking():
    canvas.itemconfig(punchline_text_id, text=current_joke[1])
    canvas.itemconfig(status_text_id, text="")
    play_sound(sfx_punchline)
    animate_punch_pop()
    animate_punch_shake()


# =====================
#  LOGIC FUNCTIONS
# =====================
def show_joke():
    global current_joke
    if not jokes:
        current_joke = ("No jokes available?", "Check your randomJokes.txt file!")
    else:
        current_joke = random.choice(jokes)

    canvas.itemconfig(setup_text_id, text=current_joke[0])
    canvas.itemconfig(punchline_text_id, text="")
    canvas.itemconfig(status_text_id, text="")
    play_sound(sfx_new_joke)


def show_punchline():
    # If no joke yet, pick one first
    global current_joke
    if current_joke == ("", ""):
        show_joke()

    canvas.itemconfig(punchline_text_id, text="")
    canvas.itemconfig(status_text_id, text="Alexa is thinking...")
    root.after(700, show_punchline_after_thinking)


def quit_app():
    root.destroy()


# =====================
#  COMIC BUTTON CREATOR (HORIZONTAL-FRIENDLY)
# =====================
def make_comic_button(text, cmd, cx, cy,
                      bg_color="#7DD3FC",       # sky blue
                      outline_color="#0C4A6E"): # dark blue outline
    btn_width = int(screen_w * 0.22)   # narrower for horizontal layout
    btn_height = 60

    x1 = cx - btn_width // 2
    y1 = cy - btn_height // 2
    x2 = cx + btn_width // 2
    y2 = cy + btn_height // 2

    rect_id = canvas.create_rectangle(
        x1, y1, x2, y2,
        fill=bg_color,
        outline=outline_color,
        width=5
    )

    btn = tk.Button(
        root,
        text=text,
        command=cmd,
        font=BUTTON_FONT,
        bg=bg_color,
        fg="black",
        activebackground="#BAE6FD",
        activeforeground="black",
        relief="flat",
        bd=0
    )
    canvas.create_window(cx, cy, window=btn)

    # Hover effects
    def on_enter(e):
        canvas.itemconfig(rect_id, outline="#38BDF8")
        btn.config(bg="#E0F2FE")

    def on_leave(e):
        canvas.itemconfig(rect_id, outline=outline_color)
        btn.config(bg=bg_color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn


# =====================
#  BUTTON POSITIONS (HORIZONTAL)
# =====================
buttons_y = int(screen_h * 0.72)

# 3 buttons side-by-side
spacing = int(screen_w * 0.24)  # distance between centers

btn_x_center = center_x
btn_x_left = center_x - spacing
btn_x_right = center_x + spacing

make_comic_button("Alexa tell me a Joke", show_joke,      btn_x_left,   buttons_y)
make_comic_button("Show Punchline",       show_punchline, btn_x_center, buttons_y)
make_comic_button("Next Joke",            show_joke,      btn_x_right,  buttons_y)

# Quit button (bottom right corner)
quit_btn = tk.Button(
    root,
    text="QUIT",
    command=quit_app,
    font=("Arial", 14, "bold"),
    bg="#F44336",
    fg="white",
    activebackground="#E53935",
    relief="flat",
    bd=0,
    padx=10,
    pady=3
)
canvas.create_window(screen_w - 90, screen_h - 50, window=quit_btn)

root.mainloop()
