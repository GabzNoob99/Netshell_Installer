import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import ctypes
import sys
import os
from installer import instalar
import re

# --- Verificar admin NO INÍCIO ---
try:
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
except Exception:
    pass

# --- Helpers ---

def carregar_imagem(nome, size=(64, 64)):
    path = os.path.join(os.path.dirname(__file__), nome)
    try:
        from PIL import Image, ImageTk
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        try:
            return tk.PhotoImage(file=path)
        except Exception:
            return None


# --- Janela principal ---
janela = tk.Tk()
janela.title("Instalador NetShell")
janela.geometry("720x480")

# Tema
BG = "#0f1724"
CARD = "#0b1220"
FG = "#e6eef8"
MUTED = "#9aa6bb"
PRIMARY = "#6ea8fe"
ACCENT = "#ffffff"
FONT = ("Segoe UI", 10)
HEADER_FONT = ("Segoe UI", 16, "bold")
SUB_FONT = ("Segoe UI", 11)

janela.configure(bg=BG)

# Progressbar style
style = ttk.Style(janela)
try:
    style.theme_use("clam")
except Exception:
    pass
style.configure("blue.Horizontal.TProgressbar", troughcolor="#081126", background=PRIMARY, thickness=18)

# Pages container
pages = {}
current_page = None


def show_page(name):
    global current_page
    if current_page:
        current_page.pack_forget()
    current_page = pages[name]
    current_page.pack(fill="both", expand=True, padx=20, pady=20)


# --- Page 1: Welcome / Info ---
page1 = tk.Frame(janela, bg=BG)
pages["welcome"] = page1

# Conteúdo principal
content_frame = tk.Frame(page1, bg=BG)
content_frame.pack(fill="both", expand=True)

left = tk.Frame(content_frame, bg=BG)
left.pack(side="left", fill="y", padx=(0, 20))

ico_big = carregar_imagem("ico.png", (96, 96))
if ico_big:
    tk.Label(left, image=ico_big, bg=BG).pack(pady=6)

tk.Label(left, text="Olá!", bg=BG, fg=PRIMARY, font=HEADER_FONT).pack(anchor="w")
tk.Label(left, text="Bem-vindo ao instalador do NetShell.", bg=BG, fg=FG, font=SUB_FONT).pack(anchor="w", pady=(4, 12))

right = tk.Frame(content_frame, bg=CARD)
right.pack(side="left", fill="both", expand=True)

tk.Label(right, text="Informações do NetShell", bg=CARD, fg=PRIMARY, font=HEADER_FONT).pack(anchor="w", padx=12, pady=(8, 4))

info_text = tk.Text(right, bg=CARD, fg=FG, bd=0, wrap="word", font=SUB_FONT, height=14)
info_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
info_text.configure(state="normal")

info = """NetShell é um shell desenvolvido inteiramente em Python, criado com o objetivo de fornecer uma experiência simples e rápida para execução de comandos. O projeto possui seu próprio shell, e depende de um terminal. Inspirado nos terminais bash, O NetShell continua em desenvolvimento e recebe melhorias constantes a cada versão.
✔ Desenvolvido 100% em Python
✔ Código aberto (Open Source)
✔ Leve e rápido
✔ Fácil de usar, junto com o comando "help"
✔ Projeto em constante evolução"""
info_text.insert("1.0", info)
info_text.configure(state="disabled")

# Botões de navegação (footer)
btn_welcome = tk.Frame(page1, bg=BG)
btn_welcome.pack(fill="x", pady=(8, 0))
tk.Button(btn_welcome, text="← Anterior", bg=CARD, fg=FG, font=SUB_FONT, padx=12, pady=6, state="disabled").pack(side="left")
tk.Button(btn_welcome, text="Próximo →", bg=PRIMARY, fg=BG, font=SUB_FONT, padx=12, pady=6, command=lambda: show_page("folder")).pack(side="right")


# --- Page 2: Folder selection ---
page2 = tk.Frame(janela, bg=BG)
pages["folder"] = page2

tk.Label(page2, text="Escolha a pasta de instalação", bg=BG, fg=PRIMARY, font=HEADER_FONT).pack(anchor="w")

frame_folder = tk.Frame(page2, bg=BG)
frame_folder.pack(fill="x", pady=12)

entrada_pasta = tk.Entry(frame_folder, font=SUB_FONT, bd=1, relief="solid")
entrada_pasta.pack(side="left", fill="x", expand=True, padx=(0, 8))


def escolher_pasta_ui():
    pasta = filedialog.askdirectory()
    if pasta:
        entrada_pasta.delete(0, tk.END)
        entrada_pasta.insert(0, pasta)

btn_escolher = tk.Button(frame_folder, text="Escolher...", command=escolher_pasta_ui, bg=CARD, fg=FG, font=SUB_FONT)
btn_escolher.pack(side="left")

nav = tk.Frame(page2, bg=BG)
nav.pack(fill="x", pady=(12, 0))
tk.Button(nav, text="← Anterior", command=lambda: show_page("welcome"), bg=CARD, fg=FG, font=SUB_FONT, padx=12, pady=6).pack(side="left")
tk.Button(nav, text="Próximo →", command=lambda: show_page("progress"), bg=PRIMARY, fg=BG, font=SUB_FONT, padx=12, pady=6).pack(side="right")


# --- Page 3: Progress and logs ---
page3 = tk.Frame(janela, bg=BG)
pages["progress"] = page3

tk.Label(page3, text="Instalação", bg=BG, fg=PRIMARY, font=HEADER_FONT).pack(anchor="w")

prog = ttk.Progressbar(page3, style="blue.Horizontal.TProgressbar", orient="horizontal", mode="determinate", maximum=100)
prog.pack(fill="x", pady=12)

log_box = tk.Text(page3, height=12, bg="#061225", fg=FG, bd=0, font=("Consolas", 10))
log_box.pack(fill="both", expand=True, pady=(0, 8))
log_box.configure(state="disabled")


def append_log(text):
    log_box.configure(state="normal")
    log_box.insert("end", text + "\n")
    log_box.see("end")
    log_box.configure(state="disabled")


def installer_callback(msg):
    if isinstance(msg, str) and msg.startswith("PROGRESS:"):
        try:
            pct = int(msg.split(":", 1)[1])
            prog["value"] = pct
        except Exception:
            pass
    else:
        append_log(msg)

controls = tk.Frame(page3, bg=BG)
controls.pack(fill="x", pady=(12, 0))
tk.Button(controls, text="← Anterior", bg=CARD, fg=FG, font=SUB_FONT, padx=12, pady=6, command=lambda: show_page("folder")).pack(side="left")


def start_install():
    pasta = entrada_pasta.get().strip()
    if not pasta:
        messagebox.showerror("Erro", "Escolha uma pasta de instalação antes de prosseguir.")
        return

    try:
        os.makedirs(pasta, exist_ok=True)
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível criar a pasta: {e}")
        return

    log_box.configure(state="normal")
    log_box.delete("1.0", "end")
    log_box.configure(state="disabled")
    prog["value"] = 0

    def run():
        def cb(m):
            janela.after(1, installer_callback, m)

        instalar(pasta, cb)
        janela.after(200, lambda: show_page("done"))

    threading.Thread(target=run, daemon=True).start()

nav_end = tk.Frame(page3, bg=BG)
nav_end.pack(fill="x", pady=(6, 0))
tk.Button(nav_end, text="Próximo", bg=PRIMARY, fg=BG, font=SUB_FONT, padx=12, pady=6, state="disabled").pack(side="right")
btn_start = tk.Button(controls, text="Iniciar Instalação", bg=PRIMARY, fg=BG, font=SUB_FONT, command=start_install)
btn_start.pack(side="right")

# --- Page 4: Final ---
page4 = tk.Frame(janela, bg=BG)
pages["done"] = page4

tk.Label(page4, text="Obrigado por instalar!", bg=BG, fg=PRIMARY, font=HEADER_FONT).pack(pady=20)
tk.Label(page4, text="NetShell foi instalado com sucesso.", bg=BG, fg=FG, font=SUB_FONT).pack()
tk.Label(page4, text="Já pode fechar esta janela.", bg=BG, fg=FG, font=SUB_FONT).pack()

btn_final = tk.Frame(page4, bg=BG)
btn_final.pack(fill="x", pady=(20, 0))
tk.Button(btn_final, text="← Anterior", command=lambda: show_page("progress"), bg=CARD, fg=FG, font=SUB_FONT, padx=12, pady=6).pack(side="left")
tk.Button(btn_final, text="Fechar", command=janela.destroy, bg=PRIMARY, fg=BG, font=SUB_FONT, padx=12, pady=6).pack(side="right")

# Inicia na página de boas-vindas
show_page("welcome")

janela.mainloop()
