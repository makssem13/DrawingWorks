THIS_PROGRAM_VER = 0.7

from tkinter import *
from tkinter import colorchooser, filedialog, simpledialog, messagebox
from recanvas import reCanvas
from jinja2 import Template
import pickle
import msgpack
import sys

from . import cms, shape

root = Tk()
root.title(f"DrawingWorks Alpha {THIS_PROGRAM_VER}")
root.geometry("800x600")

canvas = reCanvas(root, width=800, height=600, bg="white")
canvas.pack()
canvas.update()
root.update()

ST_BAR = Template("Main color: {{mc}} Secondary color: {{sc}}\nPoint radius: {{pr.ljust(5)}} Line width: {{lw}}\nHold-draw: {% if hd %}Enabled {% else %}Disabled{% endif %} Help - ?")
#defaults
DCOLOR = "#000000"
DOUTL = "#000000"
DRADP = 3
DWIDTH = 1
DHOLD = True

COLOR = DCOLOR
OUTL = DOUTL
RADP = DRADP
WIDTH = DWIDTH
HOLD = DHOLD
LOG = True

IMAGE_FILE = ""
POINTS_FILE = ""
PROJECT_FILE = ""

all_points = []
points = []
log = []
undo_log = []

class ProjectError(Exception):
    def __init__(self, ostr):
        super().__init__(ostr)

def add_log(ln):
    if LOG:
        log.append(ln)
        undo_log.clear()

def nearest(p, pts):
    x, y = p
    best = None
    best_dist = float("inf")
    for px, py in pts:
        dist = (x - px)**2 + (y - py)**2
        if dist < best_dist:
            best_dist = dist
            best = [px, py]
    return best

def render(sh):
    match sh.Type:
        case shape.ShapeType.POINT:
            x = sh.points[0]
            y = sh.points[1]
            r = sh.Radius
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=sh.FillColor.get_hex(), outline=sh.FillColor.get_hex())
        case shape.ShapeType.LINE:
            canvas.create_line(shapes[sh.points[0]].points[0], shapes[sh.points[0]].points[1], shapes[sh.points[1]].points[0], shapes[sh.points[1]].points[1], fill=sh.FillColor, width=sh.BorderWidth)
        case shape.ShapeType.POLYGON:
            coords = [shapes[sh.points[x]][0], shapes[sh.points[x]][1] for x in range(len(sh.points))]
            match sh.NoFill:
                case False:
                    canvas.create_polygon(coords, fill=sh.FillColor.get_hex(), outline=sh.BorderColor.get_hex(), width=sh.BorderWidth)
                case True:
                    for x in range(0, len(coords), 2):
                        canvas.create_line(coords[x], coords[x+1], coords[x+2], coords[x+3], fill=sh.FillColor.get_hex(), width=sh.BorderWidth)
                    canvas.create_line(coords[0], coords[1], coords[-2], coords[-1], fill=sh.FillColor.get_hex(), width=sh.BorderWidth)


def draw(event):
    global points, all_points
    if event.state & 0x0001:
        points.append(nearest([event.x, event.y], all_points))
        add_log(["NEAR", event.x, event.y])
        return
    x = event.x
    y = event.y
    points.append([x, y])
    all_points.append([x, y])
    add_log(["DOT", event.x, event.y])
    r = RADP
    canvas.create_oval(
        x-r, y-r,
        x+r, y+r,
        fill=COLOR,
        outline=COLOR)

def draw_hold(event):
    if HOLD: draw(event)

def cp(m): # cp = Color Picker, m = is Main color
    global COLOR, OUTL
    c = colorchooser.askcolor(title="Choose color")[1]
    if c != None:
        if m == True:
            COLOR = c
            add_log(["MCOLOR", c])
        else:
            OUTL = c
            add_log(["SCOLOR", c])

def rp(event): # Radius Picker
    global RADP
    try:
        RADP = int(simpledialog.askstring("Set radius", "Enter radius of points in pixels:"))
        add_log(["RAD", RADP])
    except: pass

def wp(event): # Width Picker
    global WIDTH
    try:
        WIDTH = int(simpledialog.askstring("Set width", "Enter width of a line in pixels:"))
        add_log(["WIDTH", WIDTH])
    except: pass

def change_hold(event):
    global HOLD
    HOLD = False if HOLD else True
    if LOG: log.append(["HOLD", HOLD])

def fill(event):
    global points
    changed = False
    if len(points) >= 3:
        canvas.create_polygon(
            points,
            fill=COLOR,
            outline=OUTL,
            width=WIDTH)
        changed = True
    elif len(points) == 2:
        canvas.create_line(points[0][0], points[0][1], points[1][0], points[1][1], fill=OUTL, width=WIDTH)
        changed = True
    
    if changed:
        points = []
        add_log(["FILL"])

def line(event):
    global points
    if len(points) >= 2:
        for x in range(0, len(points)-1):
            canvas.create_line(points[x][0], points[x][1], points[x+1][0], points[x+1][1], fill=OUTL, width=WIDTH)
        points = []
        add_log(["LINE"])

def stroke(event):
    global points
    if len(points) >= 2:
        for x in range(0, len(points)-1):
            canvas.create_line(points[x][0], points[x][1], points[x+1][0], points[x+1][1], fill=OUTL, width=WIDTH)
        canvas.create_line(points[0][0], points[0][1], points[-1][0], points[-1][1], fill=OUTL, width=WIDTH)
        points = []
        add_log(["STROKE"])

def clear_fill(event):
    global points
    points = []
    add_log(["CFILL"])

def rerender_all():
    global COLOR, OUTL, RADP, WIDTH, HOLD, LOG
    COLOR = DCOLOR
    OUTL = DOUTL
    RADP = DRADP
    WIDTH = DWIDTH
    HOLD = DHOLD
    canvas.clear()
    points.clear()
    all_points.clear()
    LOG = False
    for com in log:
        match com[0]:
            case "NEAR":
                points.append(nearest([com[1], com[2]], all_points))
            case "DOT":
                x = com[1]
                y = com[2]
                r = RADP
                canvas.create_oval(
                    x-r, y-r,
                    x+r, y+r,
                    fill=COLOR,
                    outline=COLOR)
                points.append([x, y])
                all_points.append([x, y])
            case "MCOLOR":
                COLOR = com[1]
            case "SCOLOR":
                OUTL = com[1]
            case "RAD":
                RADP = com[1]
            case "WIDTH":
                WIDTH = com[1]
            case "HOLD":
                HOLD = com[1]
            case "FILL":
                fill(event=None)
            case "LINE":
                line(event=None)
            case "STROKE":
                stroke(event=None)
            case "CFILL":
                clear_fill(event=None)
    LOG = True

def pack_log():
    return {"prog": "DrawingWorks", "ver": THIS_PROGRAM_VER, "log": log}

def unpack_log(packed):
    global log
    if packed["prog"] != "DrawingWorks": raise ProjectError("The file is not a DrawingWorks project.")
    if packed["ver"] > THIS_PROGRAM_VER: raise ProjectError("This version may not support the project file. Please consider updating your program.")
    log = packed["log"]

def save_image(event):
    global IMAGE_FILE
    if not IMAGE_FILE: dest = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")], title="Destination filename")
    else: dest = IMAGE_FILE
    if dest != "":
        canvas.get_buf().save(dest)
        IMAGE_FILE = dest

def open_image(event):
    global IMAGE_FILE
    file = filedialog.askopenfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")], title="Open image")
    if file != "":
        canvas.open_image_as_buf(file)
        IMAGE_FILE = file

def save_all_points(event):
    global POINTS_FILE
    if not POINTS_FILE: dest = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("DAT Files", "*.dat"), ("All files", "*.*")], title="Destination filename")
    else: dest = POINTS_FILE
    if dest != "":
        with open(dest, "wb") as f: pickle.dump(all_points, f)
        POINTS_FILE = dest

def load_all_points(event):
    global all_points, POINTS_FILE
    file = filedialog.askopenfilename(defaultextension=".dat", filetypes=[("DAT Files", "*.dat"), ("All files", "*.*")], title="Open file filename")
    if file != "":
        with open(file, "rb") as f: all_points = pickle.load(f)
        POINTS_FILE = file

def save_project(event):
    global PROJECT_FILE
    if not PROJECT_FILE: dest = filedialog.asksaveasfilename(defaultextension=".dwp", filetypes=[("DrawingWorks Project files", "*.dwp"), ("All files", "*.*")], title="Save project as")
    else: dest = PROJECT_FILE
    if dest != "":
        with open(dest, "wb") as f: msgpack.dump(pack_log(), f)
        PROJECT_FILE = dest

def load_project(event):
    global PROJECT_FILE
    if not PROJECT_FILE: file = filedialog.askopenfilename(defaultextension=".dwp", filetypes=[("DrawingWorks Project files", "*.dwp"), ("All files", "*.*")], title="Open project")
    else: file = PROJECT_FILE
    if file != "":
        with open(file, "rb") as f: data = msgpack.load(f)
        try:
            unpack_log(data)
        except ProjectError as e:
            messagebox.showerror("Project import error", e)
        except Exception as e:
            messagebox.showerror("Project import error", f"The project file is corrupted. Error: {e}")
        rerender_all()
        PROJECT_FILE = file

def undo(event):
    if log != []:
        undo_log.append(log.pop())
        rerender_all()

def redo(event):
    if undo_log != []:
        log.append(undo_log.pop())
        rerender_all()

def get_help(event):
    messagebox.showinfo("Help",
                        """Controls:
Click 1 (left mouse button): draw point
Hold 1: draw points
Shift + Click 1: add the nearest point to fill buffer (snap)
c - choose main color
v - choose secondary (outline) color
f - fill (with Shift - stroke) (automatically empties points buffer)
d - line (automatically empties points buffer)
r - set point size (with Shift - set line width)
m - enable or disable hold draw
n - clear fill buffer
Ctrl+z - undo
Ctrl+Shift+z - redo
? - get help

Files operations:
Ctrl+a - load project
Ctrl+s - save project
Ctrl+e - export image (you cannot convert them to a project!)
Ctrl+Shift+e - import image

Deprecated:
Ctrl+Alt+e - save snap data
Ctrl+Alt+Shift+e - load snap data

The deprecated functions aren't supported. They may have bugs or security vulnerabilities and we don't recommend their usage. Use them on your own risks!""")

canvas.focus_set()

status_text = StringVar()
status_bar = Label(canvas.canvas, textvariable=status_text, justify="left", bg="#FFFFFF", fg="#000000", anchor="w", font=("Consolas", 8))
status_bar.place(relx=1, rely=1, x=-10, y=-10, anchor="se", height=48)

canvas.bind("<Button-1>", draw)
canvas.bind("<B1-Motion>", draw_hold)
canvas.bind("c", lambda event: cp(True))
canvas.bind("v", lambda event: cp(False))
canvas.bind("f", fill)
canvas.bind("F", stroke)
canvas.bind("d", line)
canvas.bind("r", rp)
canvas.bind("R", wp)
canvas.bind("<Control-z>", undo)
canvas.bind("<Control-Z>", redo)
canvas.bind("<Control-E>", open_image)
canvas.bind("<Control-e>", save_image)
canvas.bind("<Control-Alt-E>", load_all_points)
canvas.bind("<Control-Alt-e>", save_all_points)
canvas.bind("<Control-a>", load_project)
canvas.bind("<Control-s>", save_project)
canvas.bind("m", change_hold)
canvas.bind("n", clear_fill)
canvas.bind("?", get_help)

if len(sys.argv) > 1:
    PROJECT_FILE = sys.argv[1]
    load_project(event=None)

def update_status_bar():
    global status_text
    status_text.set(ST_BAR.render(mc=str(COLOR), sc=str(OUTL), pr=str(RADP), lw=str(WIDTH), hd=HOLD))

def update():
    update_status_bar()
    canvas.update()
    root.after(int(1000/60), update)

update()
root.mainloop()
