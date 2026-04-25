import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta
import threading
import time
import json
import os
import random
import numpy as np
import pygame
import pyttsx3
import speech_recognition as sr
from pathlib import Path

# ══════════════════════════════════════════════════
#  THEME & CONSTANTS
# ══════════════════════════════════════════════════
APP_NAME  = "AI Alarm"
DATA_FILE = "alarms.json"
VERSION   = "v2.0.26"

COLORS = {
    "bg"       : "#080C18",
    "surface"  : "#0F1526",
    "card"     : "#141B2D",
    "card2"    : "#1A2540",
    "accent"   : "#7C6EFA",
    "accent2"  : "#00E5FF",
    "accent3"  : "#FF6B9D",
    "success"  : "#00FFA3",
    "warning"  : "#FFB800",
    "danger"   : "#FF4757",
    "text"     : "#EDF2FF",
    "subtext"  : "#6B7A99",
    "border"   : "#1F2D4A",
    "glow"     : "#7C6EFA33",
}

AI_QUOTES = [
    "Every morning is a new version of you. Boot up! 🚀",
    "The future belongs to those who rise early and code hard. 💻",
    "Neural pathways activated. Ready to conquer the day! 🧠",
    "Uploading motivation... 100% complete. Let's go! ⚡",
    "Your dreams don't work unless you do. Rise up! 🌟",
    "Another day, another algorithm to master. ☕",
    "The early bird gets the bandwidth. Good morning! 📡",
    "System initialized. Today's mission: Be awesome! 🎯",
    "Charging complete. You're ready to change the world! 🔋",
    "Wake up! The AI revolution needs you today. 🤖",
    "New day. New data. New opportunities. Let's process! 📊",
    "Sleep cycle complete. Cognitive functions: Optimal. 🌙",
]

ALARM_SOUNDS = {
    "⚡ Neural Pulse"  : "neural_pulse",
    "🌧 Digital Rain"  : "digital_rain",
    "🌌 Cosmic Wake"   : "cosmic_wake",
    "🤖 Cyber Beep"    : "cyber_beep",
    "🔔 Quantum Bell"  : "quantum_bell",
}

DAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYS_MINI  = ["M", "T", "W", "T", "F", "S", "S"]


# ══════════════════════════════════════════════════
#  SOUND ENGINE — numpy powered, no files needed
# ══════════════════════════════════════════════════
class SoundEngine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.sample_rate = 44100
        self.is_playing  = False
        self._thread     = None

    # ── Core waveform builder ──────────────────────
    def _wave(self, freq, duration, kind="sine", volume=0.45):
        n = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n, False)
        if kind == "sine":
            w = np.sin(2 * np.pi * freq * t)
        elif kind == "square":
            w = np.sign(np.sin(2 * np.pi * freq * t))
        elif kind == "saw":
            w = 2 * (t * freq - np.floor(t * freq + 0.5))
        elif kind == "tri":
            w = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        else:
            w = np.sin(2 * np.pi * freq * t)
        w = (w * volume * 32767).astype(np.int16)
        return np.column_stack([w, w])

    def _silence(self, duration):
        n = int(self.sample_rate * duration)
        return np.zeros((n, 2), dtype=np.int16)

    def _concat(self, parts):
        return np.concatenate(parts)

    # ── 5 Unique Alarm Sounds ─────────────────────

    def neural_pulse(self):
        """Ascending neural frequency pulse"""
        parts = []
        for freq in [330, 415, 523, 659, 830, 1046]:
            parts.append(self._wave(freq, 0.12, "sine", 0.38))
            parts.append(self._silence(0.04))
        parts.append(self._silence(0.2))
        return self._concat(parts)

    def digital_rain(self):
        """Matrix-style random digital droplets"""
        rng   = np.random.default_rng(42)
        parts = []
        for _ in range(10):
            freq = int(rng.integers(600, 2200))
            dur  = float(rng.uniform(0.04, 0.14))
            parts.append(self._wave(freq, dur, "square", 0.28))
            parts.append(self._silence(float(rng.uniform(0.02, 0.08))))
        return self._concat(parts)

    def cosmic_wake(self):
        """Rising frequency sweep — space awakening"""
        n   = int(self.sample_rate * 1.6)
        t   = np.linspace(0, 1.6, n, False)
        f   = 180 + 750 * (t / 1.6) ** 1.4
        env = np.linspace(0, 1, n) ** 0.4
        w   = np.sin(2 * np.pi * f * t) * env
        # Add shimmer harmonic
        w  += 0.2 * np.sin(2 * np.pi * f * 2 * t) * env
        w   = (w * 0.45 * 32767).astype(np.int16)
        return np.column_stack([w, w])

    def cyber_beep(self):
        """Cyberpunk SOS-style urgent beeps"""
        pattern = [
            (880, 0.08), (0, 0.06), (880, 0.08), (0, 0.06),
            (1320, 0.16), (0, 0.12), (1760, 0.08), (0, 0.25),
        ]
        parts = []
        for freq, dur in pattern:
            if freq == 0:
                parts.append(self._silence(dur))
            else:
                parts.append(self._wave(freq, dur, "square", 0.32))
        return self._concat(parts)

    def quantum_bell(self):
        """Harmonic overtone quantum chime"""
        chord  = [261.63, 329.63, 392.00, 523.25]  # C major
        n      = int(self.sample_rate * 1.2)
        t      = np.linspace(0, 1.2, n, False)
        total  = np.zeros(n)
        for i, freq in enumerate(chord):
            decay = np.exp(-2.5 * t) * (0.6 - i * 0.1)
            total += np.sin(2 * np.pi * freq * t) * decay
        total = (total / total.max() * 0.5 * 32767).astype(np.int16)
        return np.column_stack([total, total])

    # ── Playback control ──────────────────────────
    def play_sound(self, key, loop=True):
        self.stop()
        self.is_playing = True
        fn_map = {
            "neural_pulse" : self.neural_pulse,
            "digital_rain" : self.digital_rain,
            "cosmic_wake"  : self.cosmic_wake,
            "cyber_beep"   : self.cyber_beep,
            "quantum_bell" : self.quantum_bell,
        }
        fn = fn_map.get(key, self.neural_pulse)

        def _run():
            while self.is_playing:
                data  = fn()
                sound = pygame.sndarray.make_sound(data)
                sound.play()
                time.sleep(data.shape[0] / self.sample_rate + 0.25)
                if not loop:
                    self.is_playing = False
                    break

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def play_preview(self, key):
        """Non-looping preview"""
        self.play_sound(key, loop=False)

    def stop(self):
        self.is_playing = False
        pygame.mixer.stop()


# ══════════════════════════════════════════════════
#  AI ENGINE — TTS + Voice Recognition + Insights
# ══════════════════════════════════════════════════
class AIEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts        = None
        self._init_tts()

    def _init_tts(self):
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 158)
            self.tts.setProperty("volume", 0.92)
            voices = self.tts.getProperty("voices")
            for v in voices:
                if any(k in v.name.lower() for k in ["zira", "david", "english", "hazel"]):
                    self.tts.setProperty("voice", v.id)
                    break
        except Exception as e:
            print(f"[TTS] init skipped: {e}")

    def speak(self, text):
        def _go():
            try:
                if self.tts:
                    self.tts.say(text)
                    self.tts.runAndWait()
            except Exception as e:
                print(f"[TTS] error: {e}")
        threading.Thread(target=_go, daemon=True).start()

    def morning_message(self, label=""):
        now  = datetime.now()
        hour = now.hour
        day  = now.strftime("%A")
        tod  = ("Early riser! 🌙" if hour < 6 else
                "Good morning! ☀️" if hour < 12 else
                "Rise and shine! 🌤️")
        tag  = f"  •  {label}" if label else ""
        quote = random.choice(AI_QUOTES)
        return f"{tod}  {day}{tag}\n{now.strftime('%I:%M %p')}\n\n💡 {quote}"

    def listen_for_command(self, callback):
        """Background voice listener — says 'snooze' or 'stop'"""
        def _go():
            try:
                with sr.Microphone() as src:
                    self.recognizer.adjust_for_ambient_noise(src, duration=0.6)
                    audio = self.recognizer.listen(src, timeout=6, phrase_time_limit=3)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"[Voice] Heard: {text}")
                if any(w in text for w in ["snooze", "five", "later", "sleep"]):
                    callback("snooze")
                elif any(w in text for w in ["stop", "dismiss", "off", "ok", "done", "cancel"]):
                    callback("stop")
            except Exception as e:
                print(f"[Voice] {e}")
        threading.Thread(target=_go, daemon=True).start()

    def analyze_sleep(self, sleep_data):
        if not sleep_data:
            return ("🛸 No sleep data yet.\n"
                    "Start using alarms for AI-powered insights!")
        avg_snooze = (sum(d.get("snooze_count", 0) for d in sleep_data)
                      / len(sleep_data))
        recent = sleep_data[-7:]
        trend  = ([d.get("snooze_count", 0) for d in recent]
                  if len(recent) >= 2 else [])
        if avg_snooze > 3:
            return ("⚠️ High snooze rate detected!\n"
                    "AI recommends sleeping 30–45 min earlier.")
        elif avg_snooze > 1.5:
            return ("📈 Moderate snooze usage.\n"
                    "Try a consistent bedtime for deeper sleep.")
        elif trend and trend[-1] < trend[0]:
            return ("📉 Snooze count decreasing — improving trend!\n"
                    "Keep up the consistency.")
        else:
            return ("✅ Excellent wake-up consistency!\n"
                    "Your sleep schedule is well optimized.")


# ══════════════════════════════════════════════════
#  ALARM MANAGER — CRUD + JSON persistence
# ══════════════════════════════════════════════════
class AlarmManager:
    def __init__(self):
        self.alarms     = []
        self.sleep_data = []
        self._load()

    def _load(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                self.alarms     = d.get("alarms", [])
                self.sleep_data = d.get("sleep_data", [])

    def _save(self):
        with open(DATA_FILE, "w") as f:
            json.dump({"alarms": self.alarms,
                       "sleep_data": self.sleep_data}, f, indent=2)

    def add(self, hour, minute, label, sound, days):
        alarm = {
            "id"     : str(time.time()),
            "hour"   : hour,
            "minute" : minute,
            "label"  : label,
            "sound"  : sound,
            "days"   : days,
            "enabled": True,
            "snooze_count": 0,
        }
        self.alarms.append(alarm)
        self._save()
        return alarm

    def remove(self, alarm_id):
        self.alarms = [a for a in self.alarms if a["id"] != alarm_id]
        self._save()

    def toggle(self, alarm_id):
        for a in self.alarms:
            if a["id"] == alarm_id:
                a["enabled"] = not a["enabled"]
                self._save()
                return a["enabled"]

    def check_now(self):
        now = datetime.now()
        wd  = now.weekday()
        for a in self.alarms:
            if (a.get("enabled", True)
                    and a["hour"] == now.hour
                    and a["minute"] == now.minute):
                days = a.get("days", [])
                if not days or wd in days:
                    return a
        return None

    def snooze(self, alarm_id, minutes=5):
        for a in self.alarms:
            if a["id"] == alarm_id:
                a["snooze_count"] = a.get("snooze_count", 0) + 1
        self._save()
        return datetime.now() + timedelta(minutes=minutes)

    def log(self, alarm_id, snooze_count):
        self.sleep_data.append({
            "alarm_id"    : alarm_id,
            "snooze_count": snooze_count,
            "date"        : datetime.now().strftime("%Y-%m-%d"),
            "dismissed_at": datetime.now().isoformat(),
        })
        self.sleep_data = self.sleep_data[-30:]
        self._save()


# ══════════════════════════════════════════════════
#  ALARM RING WINDOW
# ══════════════════════════════════════════════════
class RingWindow(ctk.CTkToplevel):
    def __init__(self, parent, alarm, ai, sound, mgr, on_done):
        super().__init__(parent)
        self.alarm       = alarm
        self.ai          = ai
        self.sound       = sound
        self.mgr         = mgr
        self.on_done     = on_done
        self.snooze_count= alarm.get("snooze_count", 0)
        self._pulse_on   = True

        self.title("⏰ ALARM!")
        self.geometry("480x620")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg"])
        self._center(480, 620)
        self._build()
        self._tick()
        self._pulse()
        # Voice listener
        self.ai.listen_for_command(self._voice_cmd)
        # Speak greeting after 1s
        self.after(1000, lambda: self.ai.speak(
            f"Wake up! {alarm.get('label','Good morning')}!"))

    def _center(self, w, h):
        self.update_idletasks()
        x = self.winfo_screenwidth()  // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        # Glow header
        self.header = ctk.CTkLabel(
            self, text="⏰  WAKE UP!",
            font=("Courier New", 30, "bold"),
            text_color=COLORS["accent"])
        self.header.pack(pady=(30, 4))

        # Time
        self.time_lbl = ctk.CTkLabel(
            self, text=datetime.now().strftime("%I:%M:%S %p"),
            font=("Courier New", 54, "bold"),
            text_color=COLORS["text"])
        self.time_lbl.pack(pady=2)

        # Day + label
        now = datetime.now()
        ctk.CTkLabel(
            self,
            text=f"{now.strftime('%A, %d %B %Y')}",
            font=("Courier New", 13),
            text_color=COLORS["subtext"],
        ).pack()

        label = self.alarm.get("label", "Alarm")
        ctk.CTkLabel(
            self,
            text=f"🔔  {label}",
            font=("Courier New", 16, "bold"),
            text_color=COLORS["accent2"],
        ).pack(pady=(4, 18))

        # AI message card
        card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=18)
        card.pack(padx=28, fill="x", pady=(0, 16))
        msg = self.ai.morning_message(label)
        ctk.CTkLabel(
            card, text=msg,
            font=("Courier New", 12),
            text_color=COLORS["text"],
            wraplength=390, justify="center",
        ).pack(padx=20, pady=18)

        # Voice hint
        ctk.CTkLabel(
            self,
            text='🎤  Say "Snooze" or "Stop"  —  Voice Active',
            font=("Courier New", 10),
            text_color=COLORS["subtext"],
        ).pack(pady=(0, 8))

        # Snooze badge
        self.badge = ctk.CTkLabel(
            self,
            text=self._snooze_text(),
            font=("Courier New", 12),
            text_color=COLORS["warning"] if self.snooze_count else COLORS["subtext"],
        )
        self.badge.pack(pady=(0, 18))

        # Buttons
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(padx=28, fill="x")

        ctk.CTkButton(
            row, text="💤  Snooze 5 min",
            font=("Courier New", 14, "bold"),
            fg_color=COLORS["card2"],
            hover_color=COLORS["border"],
            text_color=COLORS["accent2"],
            border_width=2, border_color=COLORS["accent2"],
            height=52, corner_radius=14,
            command=self._snooze,
        ).pack(side="left", expand=True, padx=(0, 8), fill="x")

        ctk.CTkButton(
            row, text="✅  Dismiss",
            font=("Courier New", 14, "bold"),
            fg_color=COLORS["accent"],
            hover_color="#6458E8",
            height=52, corner_radius=14,
            command=self._dismiss,
        ).pack(side="right", expand=True, padx=(8, 0), fill="x")

    def _snooze_text(self):
        if self.snooze_count == 0:
            return "No snoozes yet"
        return f"💤  Snoozed {self.snooze_count}× already"

    def _tick(self):
        self.time_lbl.configure(text=datetime.now().strftime("%I:%M:%S %p"))
        self.after(1000, self._tick)

    def _pulse(self):
        col = COLORS["accent"] if self._pulse_on else COLORS["accent3"]
        self.header.configure(text_color=col)
        self._pulse_on = not self._pulse_on
        self.after(800, self._pulse)

    def _voice_cmd(self, cmd):
        if cmd == "snooze":
            self.after(0, self._snooze)
        elif cmd == "stop":
            self.after(0, self._dismiss)

    def _snooze(self):
        self.snooze_count += 1
        self.mgr.snooze(self.alarm["id"])
        self.sound.stop()
        self.on_done("snooze", self.alarm, self.snooze_count)
        self.destroy()

    def _dismiss(self):
        self.sound.stop()
        self.mgr.log(self.alarm["id"], self.snooze_count)
        self.on_done("dismiss", self.alarm, self.snooze_count)
        self.destroy()


# ══════════════════════════════════════════════════
#  ADD ALARM DIALOG
# ══════════════════════════════════════════════════
class AddAlarmDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("New Alarm")
        self.geometry("420x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.attributes("-topmost", True)
        self._center(420, 600)
        self._build()

    def _center(self, w, h):
        self.update_idletasks()
        x = self.winfo_screenwidth()  // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        ctk.CTkLabel(
            self, text="➕  New Alarm",
            font=("Courier New", 22, "bold"),
            text_color=COLORS["accent"],
        ).pack(pady=(22, 18))

        # ── Time ──────────────────────────────────
        t = self._card()
        ctk.CTkLabel(t, text="⏰  Set Time", **self._sub()).pack(anchor="w", padx=15, pady=(12, 5))
        row = ctk.CTkFrame(t, fg_color="transparent")
        row.pack(padx=15, pady=(0, 12), fill="x")

        self.h_var = tk.StringVar(value="07")
        ctk.CTkEntry(row, textvariable=self.h_var, width=62, height=42,
                     font=("Courier New", 22, "bold"), justify="center").pack(side="left")
        ctk.CTkLabel(row, text=":", font=("Courier New", 26, "bold"),
                     text_color=COLORS["text"]).pack(side="left", padx=4)
        self.m_var = tk.StringVar(value="00")
        ctk.CTkEntry(row, textvariable=self.m_var, width=62, height=42,
                     font=("Courier New", 22, "bold"), justify="center").pack(side="left")
        self.ampm = ctk.StringVar(value="AM")
        ctk.CTkSegmentedButton(
            row, values=["AM", "PM"], variable=self.ampm,
            width=95, height=42, font=("Courier New", 13, "bold"),
            selected_color=COLORS["accent"], selected_hover_color="#6458E8",
        ).pack(side="left", padx=(14, 0))

        # ── Label ─────────────────────────────────
        lf = self._card()
        ctk.CTkLabel(lf, text="📝  Label", **self._sub()).pack(anchor="w", padx=15, pady=(12, 5))
        self.label_e = ctk.CTkEntry(lf, placeholder_text="e.g., Gym, Morning Run, Class",
                                     height=38, font=("Courier New", 13))
        self.label_e.pack(padx=15, pady=(0, 12), fill="x")

        # ── Sound ─────────────────────────────────
        sf = self._card()
        ctk.CTkLabel(sf, text="🔊  Sound", **self._sub()).pack(anchor="w", padx=15, pady=(12, 5))
        self.sound_v = ctk.StringVar(value="⚡ Neural Pulse")
        ctk.CTkOptionMenu(
            sf, values=list(ALARM_SOUNDS.keys()), variable=self.sound_v,
            height=38, font=("Courier New", 12),
            fg_color=COLORS["card2"], button_color=COLORS["accent"],
        ).pack(padx=15, pady=(0, 12), fill="x")

        # ── Days ──────────────────────────────────
        df = self._card()
        ctk.CTkLabel(df, text="📅  Repeat Days (empty = one-time)",
                     **self._sub()).pack(anchor="w", padx=15, pady=(12, 6))
        days_row = ctk.CTkFrame(df, fg_color="transparent")
        days_row.pack(padx=10, pady=(0, 12))
        self.day_vars = []
        for d in DAYS_MINI:
            v = tk.BooleanVar(value=False)
            self.day_vars.append(v)
            ctk.CTkCheckBox(
                days_row, text=d, variable=v,
                width=35, checkbox_width=26, checkbox_height=26,
                font=("Courier New", 11, "bold"),
                fg_color=COLORS["accent"], checkmark_color=COLORS["text"],
            ).pack(side="left", padx=2)

        # ── Save ──────────────────────────────────
        ctk.CTkButton(
            self, text="✅  Save Alarm",
            font=("Courier New", 14, "bold"),
            fg_color=COLORS["accent"], hover_color="#6458E8",
            height=48, corner_radius=14,
            command=self._save,
        ).pack(padx=22, fill="x", pady=14)

    def _card(self):
        f = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        f.pack(padx=22, fill="x", pady=(0, 12))
        return f

    def _sub(self):
        return {"font": ("Courier New", 12), "text_color": COLORS["subtext"]}

    def _save(self):
        try:
            h = int(self.h_var.get())
            m = int(self.m_var.get())
            if self.ampm.get() == "PM" and h != 12:
                h += 12
            elif self.ampm.get() == "AM" and h == 12:
                h = 0
            label = self.label_e.get().strip() or "Alarm"
            sound = ALARM_SOUNDS[self.sound_v.get()]
            days  = [i for i, v in enumerate(self.day_vars) if v.get()]
            self.on_save(h, m, label, sound, days)
            self.destroy()
        except ValueError:
            pass


# ══════════════════════════════════════════════════
#  ALARM CARD (list item)
# ══════════════════════════════════════════════════
class AlarmCard(ctk.CTkFrame):
    def __init__(self, parent, alarm, on_toggle, on_delete, **kw):
        super().__init__(parent, fg_color=COLORS["card"],
                         corner_radius=14, **kw)
        self.alarm     = alarm
        self.on_toggle = on_toggle
        self.on_delete = on_delete
        self._build()

    def _build(self):
        h    = self.alarm["hour"]
        m    = self.alarm["minute"]
        ampm = "AM" if h < 12 else "PM"
        dh   = h % 12 or 12
        enabled = self.alarm.get("enabled", True)
        col  = COLORS["text"] if enabled else COLORS["subtext"]

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=16, pady=12, fill="y")

        ctk.CTkLabel(
            left, text=f"{dh:02d}:{m:02d}",
            font=("Courier New", 30, "bold"), text_color=col,
        ).pack(anchor="w")

        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(anchor="w")
        ctk.CTkLabel(info, text=ampm, font=("Courier New", 12),
                     text_color=COLORS["accent2"]).pack(side="left")
        lbl = self.alarm.get("label", "Alarm")
        ctk.CTkLabel(info, text=f"  •  {lbl}", font=("Courier New", 12),
                     text_color=COLORS["subtext"]).pack(side="left")

        days = self.alarm.get("days", [])
        day_str = ("  ".join(DAYS_MINI[d] for d in days)
                   if days else "One-time")
        ctk.CTkLabel(
            left, text=f"📅  {day_str}",
            font=("Courier New", 10), text_color=COLORS["subtext"],
        ).pack(anchor="w")

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=14, pady=12)

        tv = ctk.BooleanVar(value=enabled)
        ctk.CTkSwitch(
            right, text="", variable=tv,
            onvalue=True, offvalue=False,
            progress_color=COLORS["accent"],
            command=lambda: self.on_toggle(self.alarm["id"]),
        ).pack(pady=(0, 8))

        ctk.CTkButton(
            right, text="🗑", width=34, height=28,
            fg_color=COLORS["surface"],
            hover_color=COLORS["danger"],
            font=("Courier New", 13),
            corner_radius=8,
            command=lambda: self.on_delete(self.alarm["id"]),
        ).pack()


# ══════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════
class AIAlarmApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(f"{APP_NAME}  {VERSION}")
        self.geometry("480x820")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self._center(480, 820)

        self.sound = SoundEngine()
        self.ai    = AIEngine()
        self.mgr   = AlarmManager()

        self.ring_win    = None
        self.snoozed     = {}   # {alarm_id: datetime}
        self._last_check = -1   # last checked minute

        self._build_ui()
        self._tick_clock()
        self._check_loop()

    def _center(self, w, h):
        self.update_idletasks()
        x = self.winfo_screenwidth()  // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI build ──────────────────────────────────
    def _build_ui(self):
        # Header bar
        hbar = ctk.CTkFrame(self, fg_color=COLORS["surface"],
                             corner_radius=0, height=66)
        hbar.pack(fill="x")
        hbar.pack_propagate(False)

        ctk.CTkLabel(
            hbar, text="AI Alarm System",
            font=("Courier New", 20, "bold"),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=20, pady=12)

        self.clock_lbl = ctk.CTkLabel(
            hbar, text="",
            font=("Courier New", 12),
            text_color=COLORS["accent2"],
        )
        self.clock_lbl.pack(side="right", padx=18)

        # Tabs
        self.tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg"],
            segmented_button_fg_color=COLORS["surface"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color="#6458E8",
            segmented_button_unselected_color=COLORS["surface"],
            text_color=COLORS["subtext"],
            text_color_disabled=COLORS["subtext"],
        )
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add("⏰  Alarms")
        self.tabs.add("🤖  AI Insights")
        self.tabs.add("🎵  Sounds")

        self._build_alarms_tab()
        self._build_ai_tab()
        self._build_sounds_tab()

    def _build_alarms_tab(self):
        tab = self.tabs.tab("⏰  Alarms")

        ctk.CTkButton(
            tab, text="➕   Add New Alarm",
            font=("Courier New", 14, "bold"),
            fg_color=COLORS["accent"], hover_color="#6458E8",
            height=52, corner_radius=14,
            command=self._open_add_dialog,
        ).pack(padx=15, pady=14, fill="x")

        self.alarm_scroll = ctk.CTkScrollableFrame(
            tab, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
        )
        self.alarm_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 14))
        self._refresh_list()

    def _build_ai_tab(self):
        tab = self.tabs.tab("🤖  AI Insights")

        # Analysis
        ac = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=16)
        ac.pack(padx=15, pady=14, fill="x")
        ctk.CTkLabel(ac, text="🧠  AI Sleep Analysis",
                     font=("Courier New", 15, "bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=15, pady=(14, 6))
        insight = self.ai.analyze_sleep(self.mgr.sleep_data)
        ctk.CTkLabel(ac, text=insight, font=("Courier New", 12),
                     text_color=COLORS["text"], wraplength=390,
                     justify="left").pack(anchor="w", padx=15, pady=(0, 14))

        # Stats row
        sc = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=16)
        sc.pack(padx=15, pady=(0, 14), fill="x")
        ctk.CTkLabel(sc, text="📊  Your Stats",
                     font=("Courier New", 15, "bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=15, pady=(14, 8))

        total_alarms  = len(self.mgr.alarms)
        total_days    = len(self.mgr.sleep_data)
        total_snoozes = sum(d.get("snooze_count", 0) for d in self.mgr.sleep_data)
        rows = ctk.CTkFrame(sc, fg_color="transparent")
        rows.pack(padx=12, pady=(0, 14), fill="x")

        for label, val, icon in [
            ("Alarms", str(total_alarms), "⏰"),
            ("Days",   str(total_days),   "📅"),
            ("Snoozes",str(total_snoozes),"💤"),
        ]:
            b = ctk.CTkFrame(rows, fg_color=COLORS["card2"], corner_radius=12)
            b.pack(side="left", expand=True, padx=4, fill="x")
            ctk.CTkLabel(b, text=icon, font=("Courier New", 22)).pack(pady=(10, 2))
            ctk.CTkLabel(b, text=val,
                         font=("Courier New", 20, "bold"),
                         text_color=COLORS["accent2"]).pack()
            ctk.CTkLabel(b, text=label, font=("Courier New", 10),
                         text_color=COLORS["subtext"]).pack(pady=(0, 10))

        # Daily quote
        qc = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=16)
        qc.pack(padx=15, pady=(0, 14), fill="x")
        ctk.CTkLabel(qc, text="💡  Daily AI Quote",
                     font=("Courier New", 15, "bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=15, pady=(14, 6))
        ctk.CTkLabel(qc, text=random.choice(AI_QUOTES),
                     font=("Courier New", 12, "italic"),
                     text_color=COLORS["text"],
                     wraplength=390, justify="center").pack(padx=15, pady=(0, 14))

        # Refresh button
        ctk.CTkButton(
            tab, text="🔄  Refresh Insights",
            font=("Courier New", 12),
            fg_color=COLORS["card2"],
            hover_color=COLORS["border"],
            text_color=COLORS["accent2"],
            border_width=1, border_color=COLORS["accent2"],
            height=38, corner_radius=10,
            command=self._refresh_ai_tab,
        ).pack(padx=15, fill="x")

    def _build_sounds_tab(self):
        tab = self.tabs.tab("🎵  Sounds")
        ctk.CTkLabel(
            tab, text="🎵  Preview Alarm Sounds",
            font=("Courier New", 15, "bold"),
            text_color=COLORS["text"],
        ).pack(pady=(18, 8))

        for name, key in ALARM_SOUNDS.items():
            row = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12)
            row.pack(padx=15, pady=5, fill="x")
            ctk.CTkLabel(
                row, text=name,
                font=("Courier New", 13, "bold"),
                text_color=COLORS["text"],
            ).pack(side="left", padx=16, pady=14)
            ctk.CTkButton(
                row, text="▶  Play",
                width=80, height=32,
                fg_color=COLORS["accent"], hover_color="#6458E8",
                font=("Courier New", 11), corner_radius=8,
                command=lambda k=key: self.sound.play_preview(k),
            ).pack(side="right", padx=12, pady=10)

        ctk.CTkButton(
            tab, text="⏹  Stop Preview",
            font=("Courier New", 12),
            fg_color=COLORS["card2"],
            hover_color=COLORS["danger"],
            text_color=COLORS["danger"],
            border_width=1, border_color=COLORS["danger"],
            height=40, corner_radius=10,
            command=self.sound.stop,
        ).pack(padx=15, pady=14, fill="x")

    # ── Alarm list ────────────────────────────────
    def _refresh_list(self):
        for w in self.alarm_scroll.winfo_children():
            w.destroy()
        if not self.mgr.alarms:
            ctk.CTkLabel(
                self.alarm_scroll,
                text="No alarms yet.\nTap  ➕  to create your first! 🚀",
                font=("Courier New", 13),
                text_color=COLORS["subtext"],
                justify="center",
            ).pack(pady=60)
            return
        for a in sorted(self.mgr.alarms, key=lambda x: (x["hour"], x["minute"])):
            AlarmCard(
                self.alarm_scroll, a,
                on_toggle=self._toggle,
                on_delete=self._delete,
            ).pack(fill="x", pady=5)

    def _open_add_dialog(self):
        d = AddAlarmDialog(self, on_save=self._save_alarm)
        d.grab_set()

    def _save_alarm(self, h, m, label, sound, days):
        self.mgr.add(h, m, label, sound, days)
        self._refresh_list()

    def _toggle(self, aid):
        self.mgr.toggle(aid)
        self._refresh_list()

    def _delete(self, aid):
        self.mgr.remove(aid)
        self._refresh_list()

    def _refresh_ai_tab(self):
        # Rebuild AI tab with fresh data
        tab = self.tabs.tab("🤖  AI Insights")
        for w in tab.winfo_children():
            w.destroy()
        self._build_ai_tab()

    # ── Clock ─────────────────────────────────────
    def _tick_clock(self):
        self.clock_lbl.configure(
            text=datetime.now().strftime("%I:%M:%S %p  |  %a %d %b"))
        self.after(1000, self._tick_clock)

    # ── Alarm checker loop ────────────────────────
    def _check_loop(self):
        now = datetime.now()
        cur = now.hour * 60 + now.minute

        if cur != self._last_check:
            self._last_check = cur
            triggered = self.mgr.check_now()
            if triggered and self.ring_win is None:
                aid = triggered["id"]
                # Respect snooze delay
                if aid in self.snoozed:
                    if datetime.now() < self.snoozed[aid]:
                        self.after(2000, self._check_loop)
                        return
                    else:
                        del self.snoozed[aid]
                self._trigger(triggered)

        self.after(2000, self._check_loop)

    def _trigger(self, alarm):
        snd = alarm.get("sound", "neural_pulse")
        self.sound.play_sound(snd, loop=True)
        self.ring_win = RingWindow(
            self, alarm, self.ai, self.sound, self.mgr,
            on_done=self._alarm_done,
        )

    def _alarm_done(self, action, alarm, snooze_count):
        self.ring_win = None
        if action == "snooze":
            self.snoozed[alarm["id"]] = datetime.now() + timedelta(minutes=5)
        self._refresh_list()


# ══════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════
if __name__ == "__main__":
    print("""
  ╔══════════════════════════════════════════╗
  ║      AI ALARM SYSTEM 🤖⏰           ║
  ║  Voice • AI Insights • Smart Sounds      ║
  ╚══════════════════════════════════════════╝
    """)
    app = AIAlarmApp()
    app.mainloop()
