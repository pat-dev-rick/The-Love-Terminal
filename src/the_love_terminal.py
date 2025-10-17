import tkinter as tk
from gpiozero import LED, DigitalOutputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

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
else:
    root.attributes("-fullscreen", True)

root.focus_force()
root.configure(bg="black")
root.config(cursor="none")

text_color = "#00FF00"
bg_color = "black"

# Schriftgrößen und Abstände skalieren je nach Bildschirmgröße
if screen_w <= 800 or screen_h <= 600:
    header_font = ("Courier", 18, "bold")
    question_font = ("Courier", 16, "bold")
    option_font = ("Courier", 12)
    top_pad = 20
    small_pad = 6
    wrap_px = target_w - 40
else:
    header_font = ("Courier", 36, "bold")
    question_font = ("Courier", 28, "bold")
    option_font = ("Courier", 22)
    top_pad = 100
    small_pad = 10
    wrap_px = screen_w - 100

frage_label = tk.Label(root, text="", wraplength=wrap_px,
                       justify="center", fg=text_color, bg=bg_color)
frage_label.pack(pady=top_pad, padx=20, fill="x")

option1_label = tk.Label(root, text="", fg=text_color, bg=bg_color)
option1_label.pack(pady=small_pad, padx=20, fill="x")

option2_label = tk.Label(root, text="", fg=text_color, bg=bg_color)
option2_label.pack(pady=small_pad, padx=20, fill="x")

option3_label = tk.Label(root, text="", fg=text_color, bg=bg_color)
option3_label.pack(pady=small_pad, padx=20, fill="x")

root.bind("<Key>", key_pressed)

zeige_start()
root.mainloop()
