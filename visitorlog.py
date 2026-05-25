import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import re
import os

# ============================================================
#  COLOR PALETTE  –  Modern red/white theme matching screenshot
# ============================================================
C_RED_DARK    = "#8B0000"
C_RED_MID     = "#B22222"
C_RED_ACCENT  = "#CC0000"
C_RED_LIGHT   = "#F5CCCC"
C_RED_BG      = "#FFE8E8"
C_WHITE       = "#FFFFFF"
C_OFF_WHITE   = "#F8F9FA"
C_GOLD        = "#D4A017"
C_TEXT_DARK   = "#2C0000"
C_TEXT_MID    = "#7A3030"
C_TEXT_LIGHT  = "#F2CECE"
C_SIDEBAR_BG  = "#8B0000"
C_SIDEBAR_HOVER = "#6B0000"
C_NAV_ACTIVE  = "#FFFFFF"
C_NAV_ACTIVE_BG = "#A00000"
C_BORDER      = "#E0C0C0"
C_INPUT_BG    = "#FFFFFF"
C_LABEL       = "#5A1A1A"
C_GREEN       = "#006633"

# ============================================================
#  DATABASE FUNCTIONS
# ============================================================

def create_database():
    connection = sqlite3.connect("barangay_visitors.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT NOT NULL,
            contact         TEXT NOT NULL,
            address         TEXT NOT NULL,
            purpose         TEXT NOT NULL,
            visit_date      TEXT NOT NULL,
            visit_time      TEXT NOT NULL,
            person_to_see   TEXT DEFAULT ''
        )
    """)
    connection.commit()
    cursor.execute("PRAGMA table_info(visitors)")
    cols = [row[1] for row in cursor.fetchall()]
    for col, default in [('address', ''), ('person_to_see', '')]:
        if col not in cols:
            cursor.execute(f"ALTER TABLE visitors ADD COLUMN {col} TEXT DEFAULT '{default}'")
            connection.commit()
    connection.close()

def insert_visitor(full_name, contact, address, purpose, visit_date, visit_time, person_to_see=""):
    connection = sqlite3.connect("barangay_visitors.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO visitors (full_name, contact, address, purpose, visit_date, visit_time, person_to_see)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, contact, address, purpose, visit_date, visit_time, person_to_see))
    connection.commit()
    connection.close()

def get_all_visitors(search=""):
    connection = sqlite3.connect("barangay_visitors.db")
    cursor = connection.cursor()
    base = "SELECT id, full_name, contact, address, purpose, visit_date, visit_time FROM visitors"
    if search:
        like = "%" + search + "%"
        cursor.execute(base + " WHERE full_name LIKE ? OR contact LIKE ? OR purpose LIKE ? OR address LIKE ? ORDER BY id DESC",
                       (like, like, like, like))
    else:
        cursor.execute(base + " ORDER BY id DESC")
    results = cursor.fetchall()
    connection.close()
    return results

def update_visitor(visitor_id, full_name, contact, address, purpose, visit_date, visit_time, person_to_see=""):
    connection = sqlite3.connect("barangay_visitors.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE visitors SET full_name=?, contact=?, address=?, purpose=?, visit_date=?, visit_time=?, person_to_see=? WHERE id=?
    """, (full_name, contact, address, purpose, visit_date, visit_time, person_to_see, visitor_id))
    connection.commit()
    connection.close()

def count_today():
    connection = sqlite3.connect("barangay_visitors.db")
    cursor = connection.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM visitors WHERE visit_date=?", (today,))
    total = cursor.fetchone()[0]
    connection.close()
    return total

def count_all():
    connection = sqlite3.connect("barangay_visitors.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM visitors")
    total = cursor.fetchone()[0]
    connection.close()
    return total

# ============================================================
#  VALIDATION
# ============================================================

def is_valid_contact(contact):
    return bool(re.match(r"^(09|\+639)\d{9}$", contact))

def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d"); return True
    except ValueError:
        return False

def is_valid_time(time_text):
    try:
        if not re.match(r"^\d{2}:\d{2}$", time_text): return False
        datetime.strptime(time_text, "%H:%M"); return True
    except ValueError:
        return False

# ============================================================
#  ADMIN PASSWORD
# ============================================================

ADMIN_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), "admin_password.txt")

def get_admin_password():
    try:
        with open(ADMIN_PASSWORD_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() or "admin123"
    except Exception:
        return "admin123"

def save_admin_password(new_password):
    try:
        with open(ADMIN_PASSWORD_FILE, "w", encoding="utf-8") as f:
            f.write(new_password)
        return True
    except Exception:
        return False

# ============================================================
#  STYLED INPUT HELPER
# ============================================================

def make_input_field(parent, label_text, var, placeholder="", icon="", width=None, is_combo=False, combo_values=None):
    """Creates a labeled input with icon, border styling."""
    frame = tk.Frame(parent, bg=C_WHITE)
    
    # Label
    lbl_frame = tk.Frame(frame, bg=C_WHITE)
    lbl_frame.pack(fill="x", pady=(0, 4))
    if icon:
        tk.Label(lbl_frame, text=icon, font=("Segoe UI", 9),
                 bg=C_WHITE, fg=C_RED_ACCENT).pack(side="left", padx=(0, 4))
    tk.Label(lbl_frame, text=label_text,
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")
    
    # Input container with border
    input_container = tk.Frame(frame, bg=C_INPUT_BG,
                                highlightbackground=C_BORDER,
                                highlightcolor=C_RED_ACCENT,
                                highlightthickness=1)
    input_container.pack(fill="x")
    
    if is_combo and combo_values:
        style = ttk.Style()
        style.configure("Card.TCombobox",
                        fieldbackground=C_INPUT_BG,
                        background=C_WHITE,
                        foreground=C_TEXT_DARK,
                        selectbackground=C_RED_LIGHT,
                        selectforeground=C_TEXT_DARK,
                        borderwidth=0)
        style.map("Card.TCombobox",
                  fieldbackground=[("readonly", C_INPUT_BG)],
                  background=[("active", C_RED_LIGHT)])
        widget = ttk.Combobox(input_container, textvariable=var,
                              values=combo_values, state="readonly",
                              font=("Segoe UI", 10), style="Card.TCombobox")
        widget.pack(fill="x", ipady=7, padx=2)
    else:
        widget = tk.Entry(input_container, textvariable=var,
                          font=("Segoe UI", 10),
                          bg=C_INPUT_BG, fg=C_TEXT_DARK,
                          insertbackground=C_RED_ACCENT,
                          relief="flat", bd=0)
        widget.pack(fill="x", ipady=8, padx=10)
    
    def on_focus_in(e):
        input_container.config(highlightbackground=C_RED_ACCENT, highlightthickness=2)
    def on_focus_out(e):
        input_container.config(highlightbackground=C_BORDER, highlightthickness=1)
    widget.bind("<FocusIn>", on_focus_in)
    widget.bind("<FocusOut>", on_focus_out)
    
    return frame, widget


def create_rounded_card_container(parent, width, height, bg, fill, outline, radius=24, padding=12):
    """Create a rounded card background and inner content frame."""
    try:
        from PIL import Image, ImageTk, ImageDraw
        # Start fully transparent so corners outside the rounded rect are see-through
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=fill, outline=outline, width=1)
        photo = ImageTk.PhotoImage(img)
        # Canvas bg must match the parent's bg so transparency blends correctly
        parent_bg = parent["bg"]
        canvas = tk.Canvas(parent, width=width, height=height,
                           bg=parent_bg, highlightthickness=0)
        canvas.image_ref = photo
        canvas.create_image(0, 0, anchor="nw", image=photo)
        inner = tk.Frame(canvas, bg=fill)
        canvas.create_window(padding, padding, anchor="nw", window=inner,
                             width=width - 2 * padding, height=height - 2 * padding)
        return canvas, inner
    except Exception:
        frame = tk.Frame(parent, bg=fill,
                         highlightbackground=outline,
                         highlightthickness=1)
        return frame, frame


def load_icon_image_file(filename, size=18):
    icon_dir = os.path.join(os.path.dirname(__file__), "icon")
    path = os.path.join(icon_dir, filename)
    if not os.path.exists(path):
        return None
    try:
        from PIL import Image, ImageTk
        img = Image.open(path)
        if size:
            img = img.resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        try:
            return tk.PhotoImage(file=path)
        except Exception:
            return None

# ============================================================
#  LOGIN WINDOW
# ============================================================

def open_login_window(parent=None):
    login = tk.Toplevel(parent)
    login.title("Admin Login")
    width, height = 380, 280
    login.geometry(f"{width}x{height}")
    login.resizable(False, False)
    login.configure(bg=C_WHITE)
    login.update_idletasks()
    try:
        if parent:
            x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        else:
            x = (login.winfo_screenwidth() - width) // 2
            y = (login.winfo_screenheight() - height) // 2
    except Exception:
        x, y = 100, 100
    login.geometry(f"{width}x{height}+{x}+{y}")
    login.grab_set()

    # Red top bar
    top = tk.Frame(login, bg=C_RED_ACCENT, height=8)
    top.pack(fill="x")

    # Header
    header = tk.Frame(login, bg=C_RED_DARK)
    header.pack(fill="x")
    tk.Label(header, text="🔒  Administrator Login",
             font=("Georgia", 13, "bold"),
             bg=C_RED_DARK, fg=C_WHITE, pady=16).pack()

    body = tk.Frame(login, bg=C_WHITE, padx=40, pady=20)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Password",
             font=("Segoe UI", 9, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(anchor="w", pady=(0, 4))

    pw_container = tk.Frame(body, bg=C_INPUT_BG,
                             highlightbackground=C_BORDER,
                             highlightcolor=C_RED_ACCENT,
                             highlightthickness=1)
    pw_container.pack(fill="x")
    password_var = tk.StringVar()
    entry = tk.Entry(pw_container, textvariable=password_var, show="●",
                     font=("Segoe UI", 11), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                     insertbackground=C_RED_ACCENT, relief="flat", bd=0)
    entry.pack(fill="x", ipady=9, padx=10)
    entry.focus()

    def on_focus_in(e): pw_container.config(highlightbackground=C_RED_ACCENT, highlightthickness=2)
    def on_focus_out(e): pw_container.config(highlightbackground=C_BORDER, highlightthickness=1)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    result = {"success": False}

    def check_password():
        if password_var.get() == get_admin_password():
            result["success"] = True
            login.destroy()
        else:
            messagebox.showerror("Wrong Password", "Incorrect password. Try again.", parent=login)
            password_var.set("")

    btn = tk.Button(body, text="LOGIN",
                    font=("Segoe UI", 10, "bold"),
                    bg=C_RED_ACCENT, fg=C_WHITE,
                    activebackground=C_RED_DARK, activeforeground=C_WHITE,
                    relief="flat", cursor="hand2",
                    command=check_password)
    btn.pack(fill="x", pady=(16, 0), ipady=9)
    btn.bind("<Enter>", lambda e: btn.config(bg=C_RED_DARK))
    btn.bind("<Leave>", lambda e: btn.config(bg=C_RED_ACCENT))

    entry.bind("<Return>", lambda e: check_password())
    login.wait_window()
    return result["success"]

# ============================================================
#  SIDEBAR NAV ITEM
# ============================================================

def make_nav_item(sidebar, icon, text, active=False, command=None):
    bg = C_NAV_ACTIVE_BG if active else C_SIDEBAR_BG
    frame = tk.Frame(sidebar, bg=bg, cursor="hand2")
    frame.pack(fill="x", padx=0, pady=1)

    # Left accent bar for active
    if active:
        tk.Frame(frame, bg=C_GOLD, width=4).pack(side="left", fill="y")

    inner = tk.Frame(frame, bg=bg)
    inner.pack(side="left", fill="x", expand=True, padx=(12 if not active else 8), pady=10)

    tk.Label(inner, text=icon, font=("Segoe UI", 11),
             bg=bg, fg=C_WHITE).pack(side="left")
    tk.Label(inner, text=f"  {text}", font=("Segoe UI", 10, "bold" if active else "normal"),
             bg=bg, fg=C_WHITE).pack(side="left")

    def on_enter(e):
        if not active:
            frame.config(bg=C_SIDEBAR_HOVER)
            inner.config(bg=C_SIDEBAR_HOVER)
            for w in inner.winfo_children():
                w.config(bg=C_SIDEBAR_HOVER)
    def on_leave(e):
        if not active:
            frame.config(bg=C_SIDEBAR_BG)
            inner.config(bg=C_SIDEBAR_BG)
            for w in inner.winfo_children():
                w.config(bg=C_SIDEBAR_BG)

    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    inner.bind("<Enter>", on_enter)
    inner.bind("<Leave>", on_leave)
    for w in inner.winfo_children():
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)

    if command:
        for widget in [frame, inner] + list(inner.winfo_children()):
            widget.bind("<Button-1>", lambda e: command())

    return frame

# ============================================================
#  USER SCREEN  –  Modern Visitor Entry Form
# ============================================================

def show_user_screen(root, main_frame, sidebar_nav=None):
    for w in main_frame.winfo_children():
        w.destroy()

    # Update sidebar nav if available
    if sidebar_nav:
        sidebar_nav["update"]("visitor_entry")

    # ── TOP BAR ──────────────────────────────────────────────
    topbar = tk.Frame(main_frame, bg=C_RED_DARK, height=56)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    # Logo area in topbar
    left_top = tk.Frame(topbar, bg=C_RED_DARK)
    left_top.pack(side="left", padx=14, fill="y")

    logo_dir = os.path.join(os.path.dirname(__file__), "logo")
    logo_path = os.path.join(logo_dir, "logo.png")
    _top_logo = [None]

    def load_png_image(path, size=None):
        if not os.path.exists(path):
            return None
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            if size:
                img = img.resize((size, size), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            try:
                return tk.PhotoImage(file=path)
            except Exception:
                return None

    top_logo_img = load_png_image(logo_path, 50)
    if top_logo_img:
        _top_logo[0] = top_logo_img
        lbl = tk.Label(left_top, image=_top_logo[0], bg=C_RED_DARK)
        lbl.pack(side="left", padx=(0, 8))
        lbl._img = _top_logo[0]

    icon_dir = os.path.join(os.path.dirname(__file__), "icon")
    _form_icons = {}
    def load_icon_image(filename, size=18):
        icon_img = load_icon_image_file(filename, size)
        if icon_img:
            _form_icons[filename] = icon_img
        return icon_img

    title_frame = tk.Frame(left_top, bg=C_RED_DARK)
    title_frame.pack(side="left", fill="y")
    tk.Label(title_frame, text="BARANGAY SAN ANDRES",
             font=("Georgia", 11, "bold"),
             bg=C_RED_DARK, fg=C_WHITE).pack(anchor="w")
    tk.Label(title_frame, text="Visitor Log System",
             font=("Segoe UI", 8),
             bg=C_RED_DARK, fg=C_TEXT_LIGHT).pack(anchor="w")

    # Marquee strip in center
    marquee_frame = tk.Frame(topbar, bg=C_RED_DARK)
    marquee_frame.pack(side="left", expand=True, fill="y")

    marquee_inner = tk.Frame(marquee_frame, bg=C_RED_DARK)
    marquee_inner.place(relx=0.5, rely=0.5, anchor="center")

    # Decorative dots
    tk.Label(marquee_inner, text="— ✦ —  Mabuhay! Please register your visit.  — ✦ —",
             font=("Segoe UI", 9, "italic"),
             bg=C_RED_DARK, fg=C_TEXT_LIGHT).pack()

    # Admin login button
    admin_icon = load_icon_image("user.png", 18)
    admin_btn = tk.Button(topbar, text="Admin Login",
                          image=admin_icon, compound="left",
                          font=("Segoe UI", 9, "bold"),
                          bg=C_RED_MID, fg=C_WHITE,
                          activebackground=C_RED_ACCENT, activeforeground=C_WHITE,
                          relief="flat", cursor="hand2", padx=16,
                          command=lambda: try_admin_login(root, main_frame, sidebar_nav))
    if admin_icon:
        admin_btn._img = admin_icon
    admin_btn.pack(side="right", padx=14, pady=10)
    admin_btn.bind("<Enter>", lambda e: admin_btn.config(bg=C_RED_ACCENT))
    admin_btn.bind("<Leave>", lambda e: admin_btn.config(bg=C_RED_MID))

    # Gold accent line
    tk.Frame(main_frame, bg=C_GOLD, height=3).pack(fill="x")

    # ── SCROLLABLE CONTENT AREA ───────────────────────────────
    content_canvas = tk.Canvas(main_frame, bg=C_OFF_WHITE, highlightthickness=0)
    vsb = ttk.Scrollbar(main_frame, orient="vertical", command=content_canvas.yview)
    content_canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    content_canvas.pack(side="left", fill="both", expand=True)

    # Background image
    _bg_ref = [None]
    _bg_path = os.path.join(logo_dir, "barangay.png")

    def _draw_bg():
        w = content_canvas.winfo_width()
        h = content_canvas.winfo_height()
        if w < 10 or h < 10:
            return
        content_canvas.delete("bg_layer")
        try:
            from PIL import Image, ImageTk, ImageEnhance
            img = Image.open(_bg_path).convert("RGBA")
            iw, ih = img.size
            scale = max(w / iw, h / ih)
            nw, nh = int(iw * scale), int(ih * scale)
            img = img.resize((nw, nh), Image.LANCZOS)
            left = (nw - w) // 2
            top = max(0, (nh - h) // 2)
            img = img.crop((left, top, left + w, top + h))
            rgb = ImageEnhance.Brightness(img.convert("RGB")).enhance(0.55)
            photo = ImageTk.PhotoImage(rgb)
            _bg_ref[0] = photo
            content_canvas.create_image(0, 0, anchor="nw", image=photo, tags="bg_layer")
            content_canvas.tag_lower("bg_layer")
        except Exception:
            content_canvas.configure(bg=C_OFF_WHITE)


    def _on_canvas_configure(e):
        _draw_bg()

    content_canvas.bind("<Configure>", _on_canvas_configure)
    content_canvas.after(150, _draw_bg)

    # Enable mousewheel scrolling
    def _on_mousewheel(e):
        content_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    content_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ── CARD — draw rounded rect directly on content_canvas for true transparent corners ──
    CARD_W = 500
    CARD_MIN_H = 570
    CARD_RADIUS = 24

    _card_rect_id = [None]
    def _draw_card_rect(x, y, height):
        if _card_rect_id[0]:
            content_canvas.delete(_card_rect_id[0])
        x2, y2 = x + CARD_W, y + height
        r = CARD_RADIUS
        points = [
            x+r, y,  x2-r, y,
            x2, y,   x2, y+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x+r, y2,
            x, y2,   x, y2-r,
            x, y+r,  x, y,
        ]
        _card_rect_id[0] = content_canvas.create_polygon(
            points, smooth=True,
            fill=C_WHITE, outline=C_BORDER, width=1,
            tags="card_bg"
        )
        content_canvas.tag_lower("card_bg", "card_window")

    card = tk.Frame(content_canvas, bg=C_WHITE)
    card_id = content_canvas.create_window(0, 0, anchor="nw", window=card,
                                           width=CARD_W,
                                           tags="card_window")

    def _center_card(e=None):
        content_canvas.update_idletasks()
        card_h = max(CARD_MIN_H, card.winfo_reqheight())
        cw = content_canvas.winfo_width()
        ch = content_canvas.winfo_height()
        x = max(0, (cw - CARD_W) // 2)
        y = max(20, (ch - card_h) // 2)
        content_canvas.coords(card_id, x, y)
        content_canvas.itemconfig(card_id, width=CARD_W, height=card_h)
        _draw_card_rect(x, y, card_h)
        scroll_h = max(ch, card_h + y * 2)
        content_canvas.configure(scrollregion=(0, 0, cw, scroll_h))
        content_canvas.tag_lower("bg_layer")

    content_canvas.bind("<Configure>", lambda e: [_on_canvas_configure(e), _center_card(e)])
    content_canvas.after(200, _center_card)

    # Red top accent
    tk.Frame(card, bg=C_RED_ACCENT, height=6).pack(fill="x")

    # ── CARD HEADER ──────────────────────────────────────────
    header_frame = tk.Frame(card, bg=C_WHITE)
    header_frame.pack(fill="x", padx=30, pady=(20, 0))

    # Left logo
    _card_logos = [None, None]

    def _load_logo(path, size=90):
        if not os.path.exists(path):
            return None
        try:
            from PIL import Image, ImageTk
            img = Image.open(path).resize((size, size), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            try:
                return tk.PhotoImage(file=path)
            except Exception:
                return None

    logo1 = _load_logo(os.path.join(logo_dir, "logo.png"), 112)
    logo2 = _load_logo(os.path.join(logo_dir, "sk.png"), 90)
    _card_logos[0], _card_logos[1] = logo1, logo2

    left_logo_lbl = tk.Label(header_frame, bg=C_WHITE)
    if logo1:
        left_logo_lbl.config(image=logo1)
        left_logo_lbl._img = logo1
    else:
        left_logo_lbl.config(text="🏛", font=("Segoe UI", 28), fg=C_RED_DARK)
    left_logo_lbl.pack(side="left")

    center_header = tk.Frame(header_frame, bg=C_WHITE)
    center_header.pack(side="left", expand=True)

    tk.Label(center_header, text="WELCOME TO",
             font=("Georgia", 10),
             bg=C_WHITE, fg=C_TEXT_MID).pack()
    tk.Label(center_header, text="BARANGAY SAN ANDRES",
             font=("Georgia", 18, "bold"),
             bg=C_WHITE, fg=C_RED_DARK).pack()
    tk.Label(center_header, text="We're glad you're here. Please fill in your details below.",
             font=("Segoe UI", 9),
             bg=C_WHITE, fg=C_TEXT_MID).pack(pady=(4, 0))

    # Gold divider with diamond
    div_frame = tk.Frame(center_header, bg=C_WHITE, height=20)
    div_frame.pack(fill="x", pady=(8, 0))
    div_canvas = tk.Canvas(div_frame, bg=C_WHITE, height=20, highlightthickness=0)
    div_canvas.pack(fill="x")
    def draw_divider(e=None):
        w = div_canvas.winfo_width()
        if w < 10: return
        mid = w // 2
        div_canvas.delete("all")
        div_canvas.create_line(mid - 80, 10, mid - 12, 10, fill=C_GOLD, width=2)
        div_canvas.create_oval(mid - 6, 6, mid + 6, 14, fill=C_GOLD, outline=C_GOLD)
        div_canvas.create_line(mid + 12, 10, mid + 80, 10, fill=C_GOLD, width=2)
    div_canvas.bind("<Configure>", lambda e: draw_divider())

    right_logo_lbl = tk.Label(header_frame, bg=C_WHITE)
    if logo2:
        right_logo_lbl.config(image=logo2)
        right_logo_lbl._img = logo2
    else:
        right_logo_lbl.config(text="SK", font=("Segoe UI", 22, "bold"), fg=C_RED_DARK)
    right_logo_lbl.pack(side="right")

    # ── FORM ─────────────────────────────────────────────────
    form_outer = tk.Frame(card, bg=C_WHITE)
    form_outer.pack(fill="x", padx=30, pady=(20, 0))

    # Thin separator
    tk.Frame(form_outer, bg=C_BORDER, height=1).pack(fill="x", pady=(0, 20))

    purpose_options = [
        "Business / Transaction",
        "Certificate Request",
        "Complaint / Concern",
        "Clearance Application",
        "Meeting / Appointment",
        "Social Service Inquiry",
        "Other",
    ]

    name_var          = tk.StringVar()
    contact_var       = tk.StringVar()
    address_var       = tk.StringVar()
    purpose_var       = tk.StringVar(value="Select purpose of visit")
    other_purpose_var = tk.StringVar()
    
    date_var          = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    time_var          = tk.StringVar(value=datetime.now().strftime("%H:%M"))
    person_var        = tk.StringVar()
    
    # Register form variables to sync with the sidebar clock
    if sidebar_nav:
        # Access the parent scope's form_vars dictionary through root
        try:
            root.form_vars["date_var"] = date_var
            root.form_vars["time_var"] = time_var
        except Exception:
            pass

    # Row 1: Full Name + Contact
    row1 = tk.Frame(form_outer, bg=C_WHITE)
    row1.pack(fill="x", pady=(0, 16))

    name_frame = tk.Frame(row1, bg=C_WHITE)
    name_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

    name_label_frame = tk.Frame(name_frame, bg=C_WHITE)
    name_label_frame.pack(fill="x", pady=(0, 5))
    name_icon = load_icon_image("user.png", 18)
    if name_icon:
        name_icon_lbl = tk.Label(name_label_frame, image=name_icon, bg=C_WHITE)
        name_icon_lbl._img = name_icon
        name_icon_lbl.pack(side="left", padx=(0, 4))
    tk.Label(name_label_frame, text="FULL NAME *",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")
    name_container = tk.Frame(name_frame, bg=C_INPUT_BG,
                               highlightbackground=C_BORDER,
                               highlightcolor=C_RED_ACCENT,
                               highlightthickness=1)
    name_container.pack(fill="x")
    name_entry = tk.Entry(name_container, textvariable=name_var,
                          font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                          insertbackground=C_RED_ACCENT, relief="flat", bd=0)
    name_entry.pack(fill="x", ipady=9, padx=12)

    contact_frame = tk.Frame(row1, bg=C_WHITE)
    contact_frame.pack(side="left", fill="x", expand=True)

    contact_label_frame = tk.Frame(contact_frame, bg=C_WHITE)
    contact_label_frame.pack(fill="x", pady=(0, 5))
    contact_icon = load_icon_image("telephone-handle-silhouette.png", 18)
    if contact_icon:
        contact_icon_lbl = tk.Label(contact_label_frame, image=contact_icon, bg=C_WHITE)
        contact_icon_lbl._img = contact_icon
        contact_icon_lbl.pack(side="left", padx=(0, 4))
    tk.Label(contact_label_frame, text="CONTACT NUMBER *",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")
    contact_container = tk.Frame(contact_frame, bg=C_INPUT_BG,
                                  highlightbackground=C_BORDER,
                                  highlightcolor=C_RED_ACCENT,
                                  highlightthickness=1)
    contact_container.pack(fill="x")
    contact_entry = tk.Entry(contact_container, textvariable=contact_var,
                              font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                              insertbackground=C_RED_ACCENT, relief="flat", bd=0)
    contact_entry.pack(fill="x", ipady=9, padx=12)

    # Row 2: Address (full width)
    row2 = tk.Frame(form_outer, bg=C_WHITE)
    row2.pack(fill="x", pady=(0, 16))

    address_label_frame = tk.Frame(row2, bg=C_WHITE)
    address_label_frame.pack(fill="x", pady=(0, 5))
    address_icon = load_icon_image("home.png", 18)
    if address_icon:
        address_icon_lbl = tk.Label(address_label_frame, image=address_icon, bg=C_WHITE)
        address_icon_lbl._img = address_icon
        address_icon_lbl.pack(side="left", padx=(0, 4))
    tk.Label(address_label_frame, text="ADDRESS *",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")
    addr_container = tk.Frame(row2, bg=C_INPUT_BG,
                               highlightbackground=C_BORDER,
                               highlightcolor=C_RED_ACCENT,
                               highlightthickness=1)
    addr_container.pack(fill="x")
    addr_entry = tk.Entry(addr_container, textvariable=address_var,
                           font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                           insertbackground=C_RED_ACCENT, relief="flat", bd=0)
    addr_entry.pack(fill="x", ipady=9, padx=12)

    # Row 3: Purpose + Date
    row3 = tk.Frame(form_outer, bg=C_WHITE)
    row3.pack(fill="x", pady=(0, 16))

    purpose_frame = tk.Frame(row3, bg=C_WHITE)
    purpose_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

    purpose_label_frame = tk.Frame(purpose_frame, bg=C_WHITE)
    purpose_label_frame.pack(fill="x", pady=(0, 5))
    purpose_icon = load_icon_image("target.png", 18)
    if purpose_icon:
        purpose_icon_lbl = tk.Label(purpose_label_frame, image=purpose_icon, bg=C_WHITE)
        purpose_icon_lbl._img = purpose_icon
        purpose_icon_lbl.pack(side="left", padx=(0, 4))
    tk.Label(purpose_label_frame, text="PURPOSE OF VISIT *",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Card.TCombobox",
                    fieldbackground=C_INPUT_BG,
                    background=C_WHITE,
                    foreground=C_TEXT_DARK,
                    selectbackground=C_RED_LIGHT,
                    selectforeground=C_TEXT_DARK,
                    arrowcolor=C_RED_ACCENT,
                    borderwidth=0)
    style.map("Card.TCombobox",
              fieldbackground=[("readonly", C_INPUT_BG)],
              background=[("active", C_RED_LIGHT)],
              arrowcolor=[("active", C_RED_DARK)])

    purpose_container = tk.Frame(purpose_frame, bg=C_INPUT_BG,
                                  highlightbackground=C_BORDER,
                                  highlightcolor=C_RED_ACCENT,
                                  highlightthickness=1)
    purpose_container.pack(fill="x")
    purpose_combo = ttk.Combobox(purpose_container, textvariable=purpose_var,
                                  values=purpose_options, state="readonly",
                                  font=("Segoe UI", 10), style="Card.TCombobox")
    purpose_combo.pack(fill="x", ipady=6, padx=2)

    date_frame = tk.Frame(row3, bg=C_WHITE)
    date_frame.pack(side="left", fill="x", expand=True)

    date_label_frame = tk.Frame(date_frame, bg=C_WHITE)
    date_label_frame.pack(fill="x", pady=(0, 5))
    date_icon = load_icon_image("calendar.png", 18)
    if date_icon:
        date_icon_lbl = tk.Label(date_label_frame, image=date_icon, bg=C_WHITE)
        date_icon_lbl._img = date_icon
        date_icon_lbl.pack(side="left", padx=(0, 4))
    tk.Label(date_label_frame, text="VISIT DATE *",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")
    date_container = tk.Frame(date_frame, bg=C_INPUT_BG,
                               highlightbackground=C_BORDER,
                               highlightcolor=C_RED_ACCENT,
                               highlightthickness=1)
    date_container.pack(fill="x")
    date_entry = tk.Entry(date_container, textvariable=date_var,
                           font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                           insertbackground=C_RED_ACCENT, relief="flat", bd=0,
                           state="readonly")
    date_entry.pack(fill="x", ipady=9, padx=12)

    # Row 4: "Other" purpose field (hidden by default)
    other_row = tk.Frame(form_outer, bg=C_WHITE, height=0)
    other_row.pack_propagate(False)
    other_inner = tk.Frame(other_row, bg=C_WHITE)
    other_inner.pack(fill="both", expand=True)
    tk.Label(other_inner, text="✏  PLEASE SPECIFY PURPOSE *",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(anchor="w", pady=(0, 5))
    other_container = tk.Frame(other_inner, bg=C_INPUT_BG,
                                highlightbackground=C_BORDER,
                                highlightcolor=C_RED_ACCENT,
                                highlightthickness=1)
    other_container.pack(fill="x")
    other_entry = tk.Entry(other_container, textvariable=other_purpose_var,
                            font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                            insertbackground=C_RED_ACCENT, relief="flat", bd=0)
    other_entry.pack(fill="x", ipady=9, padx=12)
    other_row.pack_forget()
    other_anim_job = [None]

    def _cancel_other_animation():
        if other_anim_job[0] is not None:
            other_row.after_cancel(other_anim_job[0])
            other_anim_job[0] = None

    def _animate_other(show, current_height=None):
        _cancel_other_animation()
        target = 88
        step = 12
        if current_height is None:
            current_height = other_row.winfo_height()
        if show:
            if current_height >= target:
                other_row.configure(height=target)
                other_anim_job[0] = None
                _center_card()
                return
            next_height = min(target, current_height + step)
            other_row.configure(height=next_height)
            _center_card()
            other_anim_job[0] = other_row.after(10, lambda: _animate_other(True, next_height))
        else:
            if current_height <= 0:
                other_row.pack_forget()
                other_row.configure(height=0)
                other_anim_job[0] = None
                _center_card()
                return
            next_height = max(0, current_height - step)
            other_row.configure(height=next_height)
            _center_card()
            other_anim_job[0] = other_row.after(10, lambda: _animate_other(False, next_height))

    # Row 5: Time + Person to see
    row5 = tk.Frame(form_outer, bg=C_WHITE)
    row5.pack(fill="x", pady=(0, 16))

    time_frame = tk.Frame(row5, bg=C_WHITE)
    time_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

    time_label_frame = tk.Frame(time_frame, bg=C_WHITE)
    time_label_frame.pack(fill="x", pady=(0, 5))
    time_icon = load_icon_image("clock.png", 18)
    if time_icon:
        time_icon_lbl = tk.Label(time_label_frame, image=time_icon, bg=C_WHITE)
        time_icon_lbl._img = time_icon
        time_icon_lbl.pack(side="left", padx=(0, 4))
    tk.Label(time_label_frame, text="VISIT TIME *",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")
    time_container = tk.Frame(time_frame, bg=C_INPUT_BG,
                               highlightbackground=C_BORDER,
                               highlightcolor=C_RED_ACCENT,
                               highlightthickness=1)
    time_container.pack(fill="x")
    time_entry = tk.Entry(time_container, textvariable=time_var,
                           font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                           insertbackground=C_RED_ACCENT, relief="flat", bd=0,
                           state="readonly")
    time_entry.pack(fill="x", ipady=9, padx=12)

    person_frame = tk.Frame(row5, bg=C_WHITE)
    person_frame.pack(side="left", fill="x", expand=True)

    person_label_frame = tk.Frame(person_frame, bg=C_WHITE)
    person_label_frame.pack(fill="x", pady=(0, 5))
    person_icon = load_icon_image("user.png", 18)
    if person_icon:
        person_icon_lbl = tk.Label(person_label_frame, image=person_icon, bg=C_WHITE)
        person_icon_lbl._img = person_icon
        person_icon_lbl.pack(side="left", padx=(0, 4))
    tk.Label(person_label_frame, text="PERSON TO SEE (Optional)",
             font=("Segoe UI", 8, "bold"),
             bg=C_WHITE, fg=C_LABEL).pack(side="left")
    person_container = tk.Frame(person_frame, bg=C_INPUT_BG,
                                 highlightbackground=C_BORDER,
                                 highlightcolor=C_RED_ACCENT,
                                 highlightthickness=1)
    person_container.pack(fill="x")
    person_entry = tk.Entry(person_container, textvariable=person_var,
                             font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_MID,
                             insertbackground=C_RED_ACCENT, relief="flat", bd=0)
    person_entry.pack(fill="x", ipady=9, padx=12)

    def _toggle_other(*_):
        if purpose_var.get() == "Other":
            if not other_row.winfo_ismapped():
                other_row.pack(fill="x", pady=(0, 16), before=row5)
            _animate_other(True)
        else:
            other_purpose_var.set("")
            _animate_other(False)

    purpose_var.trace_add("write", _toggle_other)

    # Focus effects
    for entry, container in [
        (name_entry, name_container),
        (contact_entry, contact_container),
        (addr_entry, addr_container),
        (date_entry, date_container),
        (time_entry, time_container),
        (person_entry, person_container),
        (other_entry, other_container),
        (purpose_combo, purpose_container),
    ]:
        def _fi(e, c=container): c.config(highlightbackground=C_RED_ACCENT, highlightthickness=2)
        def _fo(e, c=container): c.config(highlightbackground=C_BORDER, highlightthickness=1)
        entry.bind("<FocusIn>", _fi)
        entry.bind("<FocusOut>", _fo)

    # Submit button
    btn_frame = tk.Frame(card, bg=C_WHITE, padx=30)
    btn_frame.pack(fill="x", pady=(4, 0))

    submit_btn = tk.Button(btn_frame, text="✈   REGISTER VISIT",
                           font=("Segoe UI", 12, "bold"),
                           bg=C_RED_ACCENT, fg=C_WHITE,
                           activebackground=C_RED_DARK, activeforeground=C_WHITE,
                           relief="flat", cursor="hand2")
    submit_btn.pack(fill="x", ipady=13)
    submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg=C_RED_DARK))
    submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg=C_RED_ACCENT))

    # Security notice
    notice_frame = tk.Frame(card, bg=C_WHITE)
    notice_frame.pack(fill="x", pady=(10, 24))
    tk.Label(notice_frame,
             text="🔒  Your information is secure and will be used for barangay records only.",
             font=("Segoe UI", 8, "italic"),
             bg=C_WHITE, fg=C_TEXT_MID).pack()

    def submit_visitor():
        name    = name_var.get().strip()
        contact = contact_var.get().strip()
        address = address_var.get().strip()
        purpose = purpose_var.get().strip()
        if purpose == "Other":
            other = other_purpose_var.get().strip()
            if other: purpose = other
        date   = date_var.get().strip()
        time   = time_var.get().strip()
        person = person_var.get().strip()

        errors = []
        if not name:    errors.append("• Full Name is required.")
        if not contact: errors.append("• Contact Number is required.")
        elif not is_valid_contact(contact): errors.append("• Contact must be 09XXXXXXXXX or +639XXXXXXXXX.")
        if not address: errors.append("• Address is required.")
        if not purpose or purpose == "Select purpose of visit":
            errors.append("• Please select a purpose of visit.")
        if purpose_var.get() == "Other" and not other_purpose_var.get().strip():
            errors.append("• Please specify the purpose of visit.")
        if not is_valid_date(date):  errors.append("• Date must be YYYY-MM-DD.")
        if not is_valid_time(time):  errors.append("• Time must be HH:MM.")

        if errors:
            messagebox.showerror("Incomplete Form", "\n".join(errors)); return

        try:
            insert_visitor(name, contact, address, purpose, date, time, person)
            messagebox.showinfo("Visit Registered! ✓",
                                f"Welcome, {name}!\n\nYour visit has been successfully logged.\nThank you for visiting Barangay San Andres.")
            name_var.set(""); contact_var.set(""); address_var.set("")
            purpose_var.set("Select purpose of visit"); other_purpose_var.set("")
            person_var.set("")
            other_row.pack_forget()
            date_var.set(datetime.now().strftime("%Y-%m-%d"))
            time_var.set(datetime.now().strftime("%H:%M"))
        except Exception as error:
            messagebox.showerror("Error", str(error))

    submit_btn.config(command=submit_visitor)


def try_admin_login(root, main_frame, sidebar_nav=None):
    if open_login_window(root):
        show_admin_screen(root, main_frame, sidebar_nav)

# ============================================================
#  ADMIN SCREEN  –  Modern Visitor Records
# ============================================================

def show_admin_screen(root, main_frame, sidebar_nav=None):
    for w in main_frame.winfo_children():
        w.destroy()

    if sidebar_nav:
        sidebar_nav["update"]("visitor_log")

    # ── TOP BAR ──────────────────────────────────────────────
    topbar = tk.Frame(main_frame, bg=C_RED_DARK, height=56)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    back_btn = tk.Button(topbar, text="← Back to Visitor Entry",
                         font=("Segoe UI", 9, "bold"),
                         bg=C_RED_MID, fg=C_WHITE,
                         activebackground=C_RED_ACCENT,
                         relief="flat", cursor="hand2", padx=14,
                         command=lambda: show_user_screen(root, main_frame, sidebar_nav))
    back_btn.pack(side="right", padx=14, pady=11)
    back_btn.bind("<Enter>", lambda e: back_btn.config(bg=C_RED_ACCENT))
    back_btn.bind("<Leave>", lambda e: back_btn.config(bg=C_RED_MID))

    tk.Label(topbar, text="  🛡  ADMIN PANEL  —  Visitor Records",
             font=("Georgia", 12, "bold"),
             bg=C_RED_DARK, fg=C_WHITE).pack(side="left", padx=16, fill="y")

    tk.Frame(main_frame, bg=C_GOLD, height=3).pack(fill="x")

    # ── STATS BAR ────────────────────────────────────────────
    stats_bar = tk.Frame(main_frame, bg=C_RED_MID, height=44)
    stats_bar.pack(fill="x")
    stats_bar.pack_propagate(False)

    stats_inner = tk.Frame(stats_bar, bg=C_RED_MID)
    stats_inner.pack(side="left", padx=20, fill="y")

    today_label = tk.Label(stats_inner,
                           text=f"📊  Today's Visitors: {count_today()}",
                           font=("Segoe UI", 9, "bold"), bg=C_RED_MID, fg=C_WHITE)
    today_label.pack(side="left", padx=(0, 20))

    tk.Frame(stats_inner, bg=C_RED_ACCENT, width=1).pack(side="left", fill="y", pady=10)

    total_label = tk.Label(stats_inner,
                           text=f"  📋  Total Records: {count_all()}",
                           font=("Segoe UI", 9, "bold"), bg=C_RED_MID, fg=C_WHITE)
    total_label.pack(side="left", padx=20)

    # ── SEARCH + ACTIONS BAR ─────────────────────────────────
    toolbar = tk.Frame(main_frame, bg=C_OFF_WHITE, pady=10)
    toolbar.pack(fill="x", padx=16)

    # Search
    search_group = tk.Frame(toolbar, bg=C_OFF_WHITE)
    search_group.pack(side="left")

    tk.Label(search_group, text="🔍", font=("Segoe UI", 11),
             bg=C_OFF_WHITE, fg=C_RED_ACCENT).pack(side="left", padx=(0, 6))

    search_var = tk.StringVar()
    search_container = tk.Frame(search_group, bg=C_WHITE,
                                 highlightbackground=C_BORDER,
                                 highlightcolor=C_RED_ACCENT,
                                 highlightthickness=1)
    search_container.pack(side="left")
    search_entry = tk.Entry(search_container, textvariable=search_var,
                             font=("Segoe UI", 10), width=28,
                             bg=C_WHITE, fg=C_TEXT_DARK,
                             relief="flat", bd=0,
                             insertbackground=C_RED_ACCENT)
    search_entry.pack(ipady=7, padx=10)
    search_entry.bind("<FocusIn>",
                      lambda e: search_container.config(highlightbackground=C_RED_ACCENT, highlightthickness=2))
    search_entry.bind("<FocusOut>",
                      lambda e: search_container.config(highlightbackground=C_BORDER, highlightthickness=1))

    record_count_var = tk.StringVar(value="")
    tk.Label(search_group, textvariable=record_count_var,
             font=("Segoe UI", 8), bg=C_OFF_WHITE, fg=C_TEXT_MID).pack(side="left", padx=10)

    # Action buttons right side
    action_group = tk.Frame(toolbar, bg=C_OFF_WHITE)
    action_group.pack(side="right")

    # Date range for export
    date_group = tk.Frame(action_group, bg=C_OFF_WHITE)
    date_group.pack(side="left", padx=(12, 0))

    tk.Label(date_group, text="From:", font=("Segoe UI", 8, "bold"),
             bg=C_OFF_WHITE, fg=C_TEXT_DARK).pack(side="left", padx=(0, 4))
    start_date_var = tk.StringVar()
    s_cont = tk.Frame(date_group, bg=C_WHITE,
                      highlightbackground=C_BORDER, highlightthickness=1)
    s_cont.pack(side="left", padx=(0, 10))
    tk.Entry(s_cont, textvariable=start_date_var, font=("Segoe UI", 9),
             width=11, bg=C_WHITE, fg=C_TEXT_DARK,
             relief="flat", bd=0).pack(ipady=5, padx=8)

    tk.Label(date_group, text="To:", font=("Segoe UI", 8, "bold"),
             bg=C_OFF_WHITE, fg=C_TEXT_DARK).pack(side="left", padx=(0, 4))
    end_date_var = tk.StringVar()
    e_cont = tk.Frame(date_group, bg=C_WHITE,
                      highlightbackground=C_BORDER, highlightthickness=1)
    e_cont.pack(side="left", padx=(0, 10))
    tk.Entry(e_cont, textvariable=end_date_var, font=("Segoe UI", 9),
             width=11, bg=C_WHITE, fg=C_TEXT_DARK,
             relief="flat", bd=0).pack(ipady=5, padx=8)

    def _run_query(query, params=()):
        conn = sqlite3.connect("barangay_visitors.db")
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def export_records():
        s = start_date_var.get().strip()
        e = end_date_var.get().strip()
        if s and not is_valid_date(s):
            messagebox.showerror("Error", "Start date must be YYYY-MM-DD."); return
        if e and not is_valid_date(e):
            messagebox.showerror("Error", "End date must be YYYY-MM-DD."); return

        if s and e:
            q = "SELECT id, full_name, contact, address, purpose, visit_date, visit_time FROM visitors WHERE visit_date BETWEEN ? AND ? ORDER BY visit_date, visit_time"
            p, rng = (s, e), f"{s} to {e}"
        elif s:
            q = "SELECT id, full_name, contact, address, purpose, visit_date, visit_time FROM visitors WHERE visit_date >= ? ORDER BY visit_date, visit_time"
            p, rng = (s,), f"from {s}"
        elif e:
            q = "SELECT id, full_name, contact, address, purpose, visit_date, visit_time FROM visitors WHERE visit_date <= ? ORDER BY visit_date, visit_time"
            p, rng = (e,), f"up to {e}"
        else:
            q = "SELECT id, full_name, contact, address, purpose, visit_date, visit_time FROM visitors ORDER BY visit_date, visit_time"
            p, rng = (), "all records"

        try:
            rows = _run_query(q, p)
        except Exception as err:
            messagebox.showerror("Error", str(err)); return

        if not rows:
            messagebox.showinfo("No Records", f"No records found for {rng}."); return

        parts = [f"Visitor Records ({rng})\nExported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"]
        for r in rows:
            id_, name, contact, address, purpose, vdate, vtime = r
            parts.append(f"ID: {id_}\nName: {name}\nContact: {contact}\nAddress: {address}\nPurpose: {purpose}\nDate: {vdate}\nTime: {vtime}\n---\n")

        fn = filedialog.asksaveasfilename(parent=root, defaultextension=".txt",
                                          filetypes=[("Text files", "*.txt")],
                                          title="Save records as...")
        if not fn: return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write("\n".join(parts))
            messagebox.showinfo("Saved", f"Records saved to:\n{fn}")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    dl_btn = tk.Button(action_group, text="⬇  Export Records",
                       bg=C_GREEN, fg=C_WHITE, font=("Segoe UI", 9, "bold"),
                       relief="flat", cursor="hand2", padx=12, pady=6,
                       command=export_records)
    dl_btn.pack(side="left", padx=4)

    # ── TABLE ────────────────────────────────────────────────
    table_outer = tk.Frame(main_frame, bg=C_WHITE,
                            highlightbackground=C_BORDER, highlightthickness=1)
    table_outer.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    columns = ("ID", "Full Name", "Contact", "Address", "Purpose", "Date", "Time")

    style2 = ttk.Style()
    style2.theme_use("clam")
    style2.configure("Modern.Treeview",
                     font=("Segoe UI", 9),
                     rowheight=32,
                     background=C_WHITE,
                     fieldbackground=C_WHITE,
                     foreground=C_TEXT_DARK,
                     borderwidth=0)
    style2.configure("Modern.Treeview.Heading",
                     font=("Segoe UI", 9, "bold"),
                     background=C_RED_DARK,
                     foreground=C_WHITE,
                     relief="flat",
                     borderwidth=0)
    style2.map("Modern.Treeview",
               background=[("selected", C_RED_LIGHT)],
               foreground=[("selected", C_RED_DARK)])

    tree = ttk.Treeview(table_outer, columns=columns,
                        show="headings", selectmode="browse",
                        style="Modern.Treeview")

    widths = {"ID": 45, "Full Name": 160, "Contact": 120,
              "Address": 185, "Purpose": 150, "Date": 95, "Time": 65}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=widths[col],
                    anchor="center" if col in ("ID", "Date", "Time") else "w",
                    minwidth=widths[col])

    tree.tag_configure("odd",  background="#FFF5F5")
    tree.tag_configure("even", background=C_WHITE)

    scrollbar = ttk.Scrollbar(table_outer, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def load_table():
        for row in tree.get_children():
            tree.delete(row)
        rows = get_all_visitors(search_var.get().strip())
        for i, row in enumerate(rows):
            tree.insert("", "end", values=row, tags=("even" if i % 2 == 0 else "odd",))
        record_count_var.set(f"{len(rows)} record(s)")
        today_label.config(text=f"📊  Today's Visitors: {count_today()}")
        total_label.config(text=f"  📋  Total Records: {count_all()}")

    search_var.trace("w", lambda *_: load_table())
    load_table()

    # ── CHANGE PASSWORD CARD (inline in admin) ────────────────
    pw_section = tk.Frame(main_frame, bg=C_OFF_WHITE)
    pw_section.pack(fill="x", padx=16, pady=(6, 12))

    pw_card = tk.Frame(pw_section, bg=C_WHITE,
                       highlightbackground=C_BORDER, highlightthickness=1)
    pw_card.pack(fill="x")
    tk.Frame(pw_card, bg=C_RED_MID, height=4).pack(fill="x")

    pw_body = tk.Frame(pw_card, bg=C_WHITE)
    pw_body.pack(fill="x", padx=24, pady=16)

    pw_left = tk.Frame(pw_body, bg=C_WHITE)
    pw_left.pack(side="left", fill="y", padx=(0, 30))
    tk.Label(pw_left, text="🔑  Change Admin Password",
             font=("Georgia", 11, "bold"),
             bg=C_WHITE, fg=C_RED_DARK).pack(anchor="w")
    tk.Label(pw_left, text="Update the password required to access this panel.",
             font=("Segoe UI", 8), bg=C_WHITE, fg=C_TEXT_MID).pack(anchor="w", pady=(4, 0))

    pw_right = tk.Frame(pw_body, bg=C_WHITE)
    pw_right.pack(side="left", fill="x", expand=True)

    pw_cur_var = tk.StringVar()
    pw_new_var = tk.StringVar()

    fields_row = tk.Frame(pw_right, bg=C_WHITE)
    fields_row.pack(fill="x")

    for label_text, var in [("Current Password", pw_cur_var), ("New Password", pw_new_var)]:
        fld = tk.Frame(fields_row, bg=C_WHITE)
        fld.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(fld, text=label_text, font=("Segoe UI", 8, "bold"),
                 bg=C_WHITE, fg=C_LABEL).pack(anchor="w", pady=(0, 4))
        cont = tk.Frame(fld, bg=C_INPUT_BG,
                        highlightbackground=C_BORDER, highlightthickness=1)
        cont.pack(fill="x")
        ent = tk.Entry(cont, textvariable=var, show="●",
                       font=("Segoe UI", 10), bg=C_INPUT_BG, fg=C_TEXT_DARK,
                       insertbackground=C_RED_ACCENT, relief="flat", bd=0)
        ent.pack(fill="x", ipady=7, padx=10)
        ent.bind("<FocusIn>",  lambda e, c=cont: c.config(highlightbackground=C_RED_ACCENT, highlightthickness=2))
        ent.bind("<FocusOut>", lambda e, c=cont: c.config(highlightbackground=C_BORDER, highlightthickness=1))

    def do_pw_change():
        if pw_cur_var.get() != get_admin_password():
            messagebox.showerror("Error", "Current password is incorrect."); return
        if len(pw_new_var.get()) < 4:
            messagebox.showerror("Error", "New password must be at least 4 characters."); return
        if save_admin_password(pw_new_var.get()):
            messagebox.showinfo("Success", "Password updated successfully.")
            pw_cur_var.set(""); pw_new_var.set("")
        else:
            messagebox.showerror("Error", "Failed to save new password.")

    upd_btn = tk.Button(pw_right, text="Update Password",
                        bg=C_RED_ACCENT, fg=C_WHITE, font=("Segoe UI", 9, "bold"),
                        relief="flat", cursor="hand2", command=do_pw_change)
    upd_btn.pack(anchor="w", pady=(10, 0), ipady=7)
    upd_btn.bind("<Enter>", lambda e: upd_btn.config(bg=C_RED_DARK))
    upd_btn.bind("<Leave>", lambda e: upd_btn.config(bg=C_RED_ACCENT))


# ============================================================
#  SETTINGS SCREEN  –  Dark Mode
# ============================================================

# Dark mode palette
DK_BG       = "#0F0F0F"
DK_SURFACE  = "#1C1C1E"
DK_SURFACE2 = "#2A2A2E"
DK_BORDER   = "#3A3A3E"
DK_TEXT     = "#F2F2F7"
DK_MUTED    = "#8E8E93"
DK_RED      = "#FF3B30"
DK_GOLD     = "#FFD60A"

def show_settings_screen(root, main_frame, sidebar_nav=None):
    for w in main_frame.winfo_children():
        w.destroy()

    if sidebar_nav:
        sidebar_nav["update"]("settings")

    # Top bar
    topbar = tk.Frame(main_frame, bg=DK_BG, height=56)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    tk.Label(topbar, text="  ⚙  SETTINGS",
             font=("Georgia", 12, "bold"),
             bg=DK_BG, fg=DK_TEXT).pack(side="left", padx=16, fill="y")
    tk.Frame(main_frame, bg=DK_GOLD, height=3).pack(fill="x")

    # Dark scrollable body
    body_canvas = tk.Canvas(main_frame, bg=DK_BG, highlightthickness=0)
    body_canvas.pack(fill="both", expand=True)

    body_inner = tk.Frame(body_canvas, bg=DK_BG)
    inner_id = body_canvas.create_window(0, 0, anchor="nw", window=body_inner)
    body_inner.bind("<Configure>", lambda e: body_canvas.configure(scrollregion=body_canvas.bbox("all")))
    body_canvas.bind("<Configure>", lambda e: body_canvas.itemconfig(inner_id, width=e.width))

    def dk_card(parent, title=None, subtitle=None):
        frame = tk.Frame(parent, bg=DK_SURFACE,
                         highlightbackground=DK_BORDER, highlightthickness=1)
        frame.pack(fill="x", padx=40, pady=(24, 0))
        tk.Frame(frame, bg=DK_RED, height=4).pack(fill="x")
        inner = tk.Frame(frame, bg=DK_SURFACE, padx=32, pady=22)
        inner.pack(fill="x")
        if title:
            tk.Label(inner, text=title, font=("Georgia", 13, "bold"),
                     bg=DK_SURFACE, fg=DK_TEXT).pack(anchor="w", pady=(0, 4))
        if subtitle:
            tk.Label(inner, text=subtitle, font=("Segoe UI", 9),
                     bg=DK_SURFACE, fg=DK_MUTED).pack(anchor="w", pady=(0, 14))
            tk.Frame(inner, bg=DK_BORDER, height=1).pack(fill="x", pady=(0, 18))
        return inner

    # ── About card ───────────────────────────────────────────
    ab = dk_card(body_inner,
                 title="About This System",
                 subtitle="Barangay San Andres — Visitor Log System")

    info_rows = [
        ("🏛  Barangay", "San Andres, Santiago City, Isabela"),
        ("💾  Version", "2.0"),
        ("🐍  Built With", "Python 3  &  SQLite"),
        ("📁  Database", "barangay_visitors.db"),
        ("🏢  Office", "Barangay Records Office"),
    ]
    for label, value in info_rows:
        row = tk.Frame(ab, bg=DK_SURFACE)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, font=("Segoe UI", 9, "bold"),
                 bg=DK_SURFACE, fg=DK_MUTED, width=18, anchor="w").pack(side="left")
        tk.Label(row, text=value, font=("Segoe UI", 9),
                 bg=DK_SURFACE, fg=DK_TEXT).pack(side="left")

    # ── Appearance card ──────────────────────────────────────
    ap = dk_card(body_inner,
                 title="Appearance",
                 subtitle="Current display settings for this application.")


    row2 = tk.Frame(ap, bg=DK_SURFACE)
    row2.pack(fill="x", pady=4)
    tk.Label(row2, text="🎨  Accent Color", font=("Segoe UI", 9, "bold"),
             bg=DK_SURFACE, fg=DK_MUTED, width=18, anchor="w").pack(side="left")
    color_dot = tk.Label(row2, text="  ●  Crimson Red  (#CC0000)", font=("Segoe UI", 9),
                          bg=DK_SURFACE, fg="#FF5555")
    color_dot.pack(side="left")

    # Spacer at bottom
    tk.Frame(body_inner, bg=DK_BG, height=40).pack()


# ============================================================
#  MAIN WINDOW SETUP
# ============================================================

def main():
    create_database()

    root = tk.Tk()
    root.title("Barangay San Andres — Visitor Log System")
    root.geometry("1100x720")
    root.minsize(900, 560)
    root.configure(bg=C_OFF_WHITE)
    try:
        root.state('zoomed')
    except Exception:
        pass

    # ── SIDEBAR ──────────────────────────────────────────────
    sidebar = tk.Frame(root, bg=C_SIDEBAR_BG, width=210)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # Top accent
    tk.Frame(sidebar, bg=C_GOLD, height=4).pack(fill="x")

    # Logo area
    logo_area = tk.Frame(sidebar, bg=C_SIDEBAR_BG)
    logo_area.pack(fill="x", pady=(20, 0))

    logo_dir = os.path.join(os.path.dirname(__file__), "logo")
    logo_path = os.path.join(logo_dir, "stgo.png")
    _sidebar_logos = [None]
    if os.path.exists(logo_path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(logo_path).resize((150, 150), Image.LANCZOS)
            _sidebar_logos[0] = ImageTk.PhotoImage(img)
            lbl = tk.Label(logo_area, image=_sidebar_logos[0], bg=C_SIDEBAR_BG)
            lbl.pack()
            sidebar.logo_img = _sidebar_logos[0]
        except Exception:
            tk.Label(logo_area, text="🏛", font=("Segoe UI", 32),
                     bg=C_SIDEBAR_BG, fg=C_WHITE).pack()
    else:
        tk.Label(logo_area, text="🏛", font=("Segoe UI", 32),
                 bg=C_SIDEBAR_BG, fg=C_WHITE).pack()

    tk.Label(sidebar, text="BARANGAY",
             font=("Georgia", 13, "bold"),
             bg=C_SIDEBAR_BG, fg=C_WHITE).pack(pady=(8, 0))
    tk.Label(sidebar, text="SAN ANDRES",
             font=("Georgia", 13, "bold"),
             bg=C_SIDEBAR_BG, fg=C_WHITE).pack()

    tk.Frame(sidebar, bg=C_GOLD, height=1).pack(fill="x", padx=20, pady=8)

    tk.Label(sidebar, text="V I S I T O R  L O G  S Y S T E M",
             font=("Segoe UI", 7, "bold"),
             bg=C_SIDEBAR_BG, fg=C_TEXT_LIGHT).pack()

    tk.Frame(sidebar, bg=C_RED_MID, height=1).pack(fill="x", padx=0, pady=12)

    # ── NAV ITEMS ─────────────────────────────────────────────
    # We'll store nav frame references for active state management
    nav_frames = {}
    main_frame_widget = None

    def main_frame_ref():
        return main_frame_widget

    sidebar_nav_state = {"current": "visitor_entry"}

    def update_nav(active_key):
        sidebar_nav_state["current"] = active_key
        for key, frame_data in nav_frames.items():
            frame = frame_data["frame"]
            inner = frame_data["inner"]
            is_active = key == active_key
            bg = C_NAV_ACTIVE_BG if is_active else C_SIDEBAR_BG
            frame.config(bg=bg)
            inner.config(bg=bg)
            for w in inner.winfo_children():
                try:
                    w.config(bg=bg)
                    if is_active:
                        w.config(fg=C_WHITE, font=("Segoe UI", 10, "bold"))
                    else:
                        w.config(fg=C_WHITE, font=("Segoe UI", 10))
                except Exception:
                    pass
            # Gold accent bar
            for w in frame.winfo_children():
                if isinstance(w, tk.Frame) and w != inner:
                    w.config(bg=C_GOLD if is_active else C_SIDEBAR_BG)

    nav_icon_images = {
        "visitor_entry": load_icon_image_file("user.png", 16),
        "visitor_log": load_icon_image_file("bullet.png", 16),
        "settings": load_icon_image_file("settings.png", 16),
    }

    nav_items = [
        ("visitor_entry", "👤", "Visitor Entry"),
        ("visitor_log", "•", "Visitor Log"),
        ("settings", "⚙", "Settings"),
    ]

    for key, icon, text in nav_items:
        is_active = key == "visitor_entry"
        bg = C_NAV_ACTIVE_BG if is_active else C_SIDEBAR_BG

        frame = tk.Frame(sidebar, bg=bg, cursor="hand2")
        frame.pack(fill="x", pady=1)

        # Gold accent bar (left)
        accent = tk.Frame(frame, bg=C_GOLD if is_active else bg, width=4)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(frame, bg=bg)
        inner.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        icon_img = nav_icon_images.get(key)
        if icon_img:
            icon_lbl = tk.Label(inner, image=icon_img, bg=bg)
            icon_lbl._img = icon_img
        else:
            icon_lbl = tk.Label(inner, text=icon, font=("Segoe UI", 11),
                                bg=bg, fg=C_WHITE)
        icon_lbl.pack(side="left")
        text_lbl = tk.Label(inner, text=f"  {text}",
                            font=("Segoe UI", 10, "bold" if is_active else "normal"),
                            bg=bg, fg=C_WHITE)
        text_lbl.pack(side="left")

        nav_frames[key] = {"frame": frame, "inner": inner, "accent": accent}

        # Hover + click
        def make_handlers(k, f, i, children):
            def on_enter(e):
                if sidebar_nav_state["current"] != k:
                    f.config(bg=C_SIDEBAR_HOVER)
                    i.config(bg=C_SIDEBAR_HOVER)
                    for w in children: w.config(bg=C_SIDEBAR_HOVER)
            def on_leave(e):
                if sidebar_nav_state["current"] != k:
                    f.config(bg=C_SIDEBAR_BG)
                    i.config(bg=C_SIDEBAR_BG)
                    for w in children: w.config(bg=C_SIDEBAR_BG)
            def on_click(e):
                if k == "visitor_entry":
                    show_user_screen(root, mf, {"update": update_nav})
                elif k == "visitor_log":
                    if open_login_window(root):
                        show_admin_screen(root, mf, {"update": update_nav})
                elif k == "settings":
                    show_settings_screen(root, mf, {"update": update_nav})
            return on_enter, on_leave, on_click

        ch = [icon_lbl, text_lbl]
        oe, ol, oc = make_handlers(key, frame, inner, ch)
        for widget in [frame, inner] + ch:
            widget.bind("<Enter>", oe)
            widget.bind("<Leave>", ol)
            widget.bind("<Button-1>", oc)

    # Gold divider
    tk.Frame(sidebar, bg=C_GOLD, height=1).pack(fill="x", padx=0, pady=(20, 8))

    # Live clock
    clock_var = tk.StringVar()
    clock_frame = tk.Frame(sidebar, bg=C_SIDEBAR_BG)
    clock_frame.pack(fill="x", padx=18)

    tk.Label(clock_frame, text="📅", font=("Segoe UI", 9),
             bg=C_SIDEBAR_BG, fg=C_GOLD).pack(side="left", padx=(0, 6))
    clock_lbl = tk.Label(clock_frame, textvariable=clock_var,
                          font=("Segoe UI", 8),
                          bg=C_SIDEBAR_BG, fg=C_TEXT_LIGHT,
                          justify="left")
    clock_lbl.pack(side="left")

    # Store form variables globally so they can be synced with the clock
    form_vars = {"date_var": None, "time_var": None}

    def update_clock():
        now = datetime.now()
        clock_var.set(f"{now.strftime('%A, %B %d, %Y')}\n{now.strftime('%I:%M:%S %p')}")
        
        # Sync form variables if they are set
        if form_vars["date_var"] is not None:
            form_vars["date_var"].set(now.strftime("%Y-%m-%d"))
        if form_vars["time_var"] is not None:
            form_vars["time_var"].set(now.strftime("%H:%M"))
            
        root.after(1000, update_clock)
    update_clock()

    # Bottom label
    tk.Frame(sidebar, bg=C_GOLD, height=1).pack(side="bottom", fill="x", pady=(0, 0))
    tk.Label(sidebar, text="Barangay Records Office\nPowered by Python & SQLite",
             font=("Segoe UI", 7), bg=C_SIDEBAR_BG, fg="#A04040",
             justify="center").pack(side="bottom", pady=12)

    # ── MAIN CONTENT ──────────────────────────────────────────
    mf = tk.Frame(root, bg=C_OFF_WHITE)
    mf.pack(side="left", fill="both", expand=True)

    # Share nav updater
    sidebar_nav = {"update": update_nav}
    main_frame_widget = mf
    
    # Attach form_vars to root so it can be accessed from show_user_screen
    root.form_vars = form_vars

    show_user_screen(root, mf, sidebar_nav)
    root.mainloop()

main()
