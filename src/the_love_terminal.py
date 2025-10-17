import tkinter as tk
from gpiozero import LED, DigitalOutputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import tkinter.font as tkfont

# =========================
# Hardware Setup
# =========================
led_gruen = LED(17)
led_rot = LED(27)
buzzer = DigitalOutputDevice(22)
factory = PiGPIOFactory()
servo = Servo(24, pin_factory=factory, min_pulse_width=0.0011, max_pulse_width=0.0019)
servo.min()  # Kästchen zu

# =========================
# Funktion: Fragen aus Datei lesen
# =========================
def lade_fragen(dateiname="fragen.txt"):
    quiz = []
    with open(dateiname, "r", encoding="utf-8") as f:
        block = {}
        for line in f:
            line = line.strip()
            if line.startswith("Frage:"):
                block["frage"] = line[7:].strip()
                block["optionen"] = []
            elif line.startswith(("1)", "2)", "3)")):
                block["optionen"].append(line)
            elif line.startswith("Antwort:"):
                block["antwort"] = int(line.split(":")[1].strip())
                quiz.append(block)
                block = {}
    return quiz

quiz = lade_fragen()
aktuelle_frage = 0
punktzahl = 0
seite = "start"

# =========================
# LEDs & Buzzer
# =========================
def richtig():
    for _ in range(3):
        led_gruen.on()
        sleep(0.2)
        led_gruen.off()
        sleep(0.2)

def falsch():
    for _ in range(3):
        led_rot.on()
        buzzer.on()
        sleep(0.15)
        led_rot.off()
        buzzer.off()
        sleep(0.1)

# =========================
# Spiellogik
# =========================
def key_pressed(event):
    global seite, aktuelle_frage, punktzahl
    key = event.keysym.lower()

    if key == "q":
        root.destroy()
        return

    if seite == "start" and key == "return":
        zeige_regeln()
        return

    if seite == "regeln" and key == "return":
        seite = "quiz"
        zeige_frage()
        return

    if seite == "quiz" and key in ["1", "2", "3"]:
        auswahl = int(key)
        if auswahl == quiz[aktuelle_frage]["antwort"]:
            punktzahl += 1
            richtig()
        else:
            falsch()
        aktuelle_frage += 1
        if aktuelle_frage < len(quiz):
            zeige_frage()
        else:
            zeige_ergebnis()
        return

    if seite == "restart" and key == "return":
        aktuelle_frage = 0
        punktzahl = 0
        seite = "quiz"
        zeige_frage()
        return

def zeige_start():
    global seite
    seite = "start"
    frage_label.config(
        text="╔════════════════════════════╗\n"
             "     THE LOVE TERMINAL ❤️     \n"
             "╚════════════════════════════╝",
        font=header_font
    )
    option1_label.config(
        text="\nWillkommen zum Hochzeitsspiel!\n"
             "Teste dein Wissen und öffne das Kästchen der Liebe.\n\n"
             "Drücke ENTER, um fortzufahren.",
        font=option_font
    )
    option2_label.config(text="")
    option3_label.config(text="")

def zeige_regeln():
    global seite
    seite = "regeln"
    frage_label.config(
        text="SPIELREGELN 💚",
        font=header_font
    )
    option1_label.config(
        text="• Beantworte jede Frage mit 1, 2 oder 3.\n"
             "• Drücke Q, um das Spiel zu beenden.\n"
             "• Nach der letzten Frage öffnet sich das Kästchen –\n"
             "  aber nur, wenn du alle Antworten richtig hast!\n\n"
             "Drücke ENTER, um zu beginnen.",
        font=option_font
    )
    option2_label.config(text="")
    option3_label.config(text="")

def zeige_frage():
    frage_label.config(
        text=quiz[aktuelle_frage]["frage"],
        font=question_font
    )
    option1_label.config(text=quiz[aktuelle_frage]["optionen"][0], font=option_font)
    option2_label.config(text=quiz[aktuelle_frage]["optionen"][1], font=option_font)
    option3_label.config(text=quiz[aktuelle_frage]["optionen"][2], font=option_font)

def zeige_ergebnis():
    global seite, aktuelle_frage, punktzahl
    seite = "ende"
    if punktzahl == len(quiz):
        servo.max()
        text = "🎉 Alle Antworten richtig!\nDas Kästchen der Liebe öffnet sich! 💖"
        frage_label.config(
            text=text,
            font=question_font
        )
        option1_label.config(text="Drücke Q, um zu beenden.", font=option_font)
        option2_label.config(text="")
        option3_label.config(text="")
    else:
        servo.min()
        text = f"Quiz beendet.\nDu hast {punktzahl}/{len(quiz)} richtig.\nDas Kästchen bleibt verschlossen. 💔\n\nDrücke ENTER, um es erneut zu versuchen."
        frage_label.config(
            text=text,
            font=question_font
        )
        option1_label.config(text="", font=option_font)
        option2_label.config(text="")
        option3_label.config(text="")
        seite = "restart"

# =========================
# GUI Setup
# =========================
root = tk.Tk()
root.title("The Love Terminal")

# Bildschirmmaße abfragen und an kleine Displays anpassen
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

# Zielauflösung für den kleinen Monitor
target_w, target_h = (640, 480)

# Wenn Display klein ist, Nutze feste Fenstergröße; sonst Vollbild
if screen_w <= target_w or screen_h <= target_h:
    root.geometry(f"{target_w}x{target_h}")
    root.resizable(False, False)
else:
    root.attributes("-fullscreen", True)

root.update_idletasks()  # aktuelle Fenstergröße wissen
root.focus_force()
root.configure(bg="black")
root.config(cursor="none")

text_color = "#00FF00"
bg_color = "black"

# Basis-Schriftgrößen (werden ggf. dynamisch verkleinert)
if screen_w <= 800 or screen_h <= 600:
    header_size = 18
    question_size = 16
    option_size = 12
    top_pad = 12
    small_pad = 4
else:
    header_size = 36
    question_size = 28
    option_size = 22
    top_pad = 60
    small_pad = 8

# --- Initiale Font-Variablen, damit zeige_start() sofort verwendet werden kann ---
header_font = ("Courier", header_size, "bold")
question_font = ("Courier", question_size, "bold")
option_font = ("Courier", option_size)

# Berechne initial wraplength aus der aktuellen Fensterbreite mit Puffer,
# damit links/rechts kein Zeichen abgeschnitten wird.
PAD_X = 12        # Label padx
SAFETY_MARGIN = 20  # extra Puffer in Pixeln, erhöht damit kein Buchstabe abgeschnitten wird

initial_width = max(200, root.winfo_width() or target_w)
wrap_px = max(100, initial_width - PAD_X * 2 - SAFETY_MARGIN)

# Labels mit Wraplength auch für Optionen
frage_label = tk.Label(root, text="", wraplength=wrap_px,
                       justify="center", fg=text_color, bg=bg_color)
frage_label.pack(pady=top_pad, padx=PAD_X, fill="x")

option1_label = tk.Label(root, text="", wraplength=wrap_px,
                         justify="center", fg=text_color, bg=bg_color)
option1_label.pack(pady=small_pad, padx=PAD_X, fill="x")

option2_label = tk.Label(root, text="", wraplength=wrap_px,
                         justify="center", fg=text_color, bg=bg_color)
option2_label.pack(pady=small_pad, padx=PAD_X, fill="x")

option3_label = tk.Label(root, text="", wraplength=wrap_px,
                         justify="center", fg=text_color, bg=bg_color)
option3_label.pack(pady=small_pad, padx=PAD_X, fill="x")

root.bind("<Key>", key_pressed)

# Resize-Handler: aktualisiert wraplength + Fonts, verhindert Abschneiden an den Seiten
def on_resize(event):
    global wrap_px
    # event.width ist die innere Breite des Fensters; großzügiger Puffer zum Rand
    wrap_px = max(80, event.width - PAD_X * 2 - SAFETY_MARGIN)
    for lbl in (frage_label, option1_label, option2_label, option3_label):
        lbl.config(wraplength=wrap_px)
    # Fonts an neue Breite/Höhe anpassen
    try:
        adjust_fonts()
    except Exception:
        pass
    # aktuelle Seite neu mit passenden Fonts rendern
    if seite in ("start", "regeln"):
        frage_label.config(font=header_font)
        option1_label.config(font=option_font)
    elif seite == "quiz":
        frage_label.config(font=question_font)
        option1_label.config(font=option_font)
        option2_label.config(font=option_font)
        option3_label.config(font=option_font)
    else:
        frage_label.config(font=question_font)
        option1_label.config(font=option_font)

# Binde Configure (Fenstergröße ändert sich) — sorgt für korrekte wraplength-Berechnung
root.bind("<Configure>", on_resize)

# Funktion: Schriftgrößen dynamisch an Inhalt & Bildschirmhöhe anpassen
def adjust_fonts():
    global header_font, question_font, option_font
    # Startwerte
    h = header_size
    q = question_size
    o = option_size
    # Minimalgrößen
    h_min, q_min, o_min = 12, 10, 8

    def total_text_height(hs, qs, os):
        fh = tkfont.Font(family="Courier", size=hs, weight="bold")
        fq = tkfont.Font(family="Courier", size=qs, weight="bold")
        fo = tkfont.Font(family="Courier", size=os)

        # Hilfsfunktion: Zeilenanzahl nach wrap berechnen
        def lines_needed(font_obj, text):
            if not text:
                return 0
            line_width = max(10, min(wrap_px, root.winfo_width() - PAD_X * 2))
            words = text.split()
            if not words:
                return 1
            lines = 0
            cur = ""
            for w in words:
                test = (cur + " " + w).strip()
                if font_obj.measure(test) <= line_width:
                    cur = test
                else:
                    lines += 1
                    cur = w
            if cur:
                lines += 1
            return lines

        h_lines = lines_needed(fh, frage_label.cget("text"))
        o1_lines = lines_needed(fo, option1_label.cget("text"))
        o2_lines = lines_needed(fo, option2_label.cget("text"))
        o3_lines = lines_needed(fo, option3_label.cget("text"))

        # Gesamtpixelhöhe = Zeilen * linespace + paddings
        total = (h_lines * fh.metrics("linespace")
                 + (o1_lines + o2_lines + o3_lines) * fo.metrics("linespace"))
        # add paddings + some margin
        total += top_pad + 3 * small_pad + 60
        return total

    # Verwende die aktuelle Fensterhöhe (nicht die ursprüngliche screen_h)
    max_height = max(100, root.winfo_height() or screen_h)

    # Verkürze solange, bis alles passt oder Minimalgrößen erreicht sind
    while (h > h_min or q > q_min or o > o_min) and total_text_height(h, q, o) > max_height - 20:
        if h > h_min:
            h -= 1
        if q > q_min:
            q -= 1
        if o > o_min:
            o -= 1

    # Setze Fonts
    header_font = ("Courier", h, "bold")
    question_font = ("Courier", q, "bold")
    option_font = ("Courier", o)

# Vor dem ersten Anzeigen: echte Starttexte setzen, dann anpassen
# (so berechnet adjust_fonts() auf realen Texten — nicht auf leeren Labels)
zeige_start()
root.update_idletasks()

# Setze initiale wraplengths basierend auf den tatsächlichen Label-Breiten,
# mit kleinem Puffer, so dass kein Buchstabe abgeschnitten wird.
for lbl in (frage_label, option1_label, option2_label, option3_label):
    w = lbl.winfo_width() or root.winfo_width()
    lbl.config(wraplength=max(10, w - 8))

# Kleine Debounce-Logik: beim Resize nicht sofort fonts zerstören
resize_after_id = None
def on_resize_debounced(event):
    global resize_after_id
    # Stelle wraplength jeweils an label-breite ein (vermeidet off-by-one)
    for lbl in (frage_label, option1_label, option2_label, option3_label):
        w = lbl.winfo_width() or event.width or root.winfo_width()
        lbl.config(wraplength=max(10, w - 8))
    # debounce adjust_fonts
    if resize_after_id:
        root.after_cancel(resize_after_id)
    resize_after_id = root.after(150, lambda: (adjust_fonts(), 
                                               frage_label.config(font=header_font if seite in ("start","regeln") else question_font),
                                               option1_label.config(font=option_font),
                                               option2_label.config(font=option_font),
                                               option3_label.config(font=option_font)))

# Überschreibe alte Bindung auf Configure
root.unbind("<Configure>")
root.bind("<Configure>", on_resize_debounced)

# Jetzt echte Fonts anpassen und Fenster starten
adjust_fonts()
zeige_start()
root.mainloop()
