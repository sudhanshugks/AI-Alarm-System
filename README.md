# 🤖 AI Alarm System

> AI-powered alarm system built for Windows. Features Voice Control, Procedural Smart Sounds & AI Sleep Insights — all in a single-click executable!

![Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-7C6EFA?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Voice%20Control-00E5FF?style=for-the-badge)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ **Voice Control** | Say "Snooze" or "Stop" to control alarms hands-free |
| 🎵 **5 Unique Sounds** | Neural Pulse, Digital Rain, Cosmic Wake, Cyber Beep, Quantum Bell |
| 🧠 **AI Sleep Analysis** | Smart pattern detection & sleep recommendations |
| 🗣️ **Text-to-Speech** | AI announces your alarm label & morning message |
| 💡 **AI Quotes** | Motivational AI-generated wake-up messages |
| 📅 **Repeat Days** | Set alarms for specific weekdays or one-time |
| 💤 **Smart Snooze** | 5-min snooze with snooze-count tracking |
| 📊 **Stats Dashboard** | Track alarms, days, and snooze history |
| 🌑 **Dark UI** | Futuristic 2026-style dark theme with Courier font |

---

## 🚀 Quick Start (No Installation Required)

You do **not** need to install Python or any dependencies to use this application!

**[🚀 Click here to Download AI Alarm.exe](https://github.com/sudhanshugks/AI-Alarm-System/releases/latest/download/AI.Alarm.exe)**
 
> ⚠️ **Browser SmartScreen Warning?** — This is normal for unsigned open-source apps.
1. Double-click the **`AI Alarm.exe`** file.
2. The app will launch immediately.

---

## 💻 For Developers (Run & Build from Source)

If you want to modify the code or build the executable yourself, follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/sudhanshugks/AI-Alarm-System.git
cd AI-Alarm-System
```

### 2. Set up virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python main.py
```

### 5. Build your own `.exe`
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name "AI Alarm" --collect-all customtkinter --collect-all pyttsx3 main.py
```
*The output file will be generated in the `dist/` directory.*

---

## 🎵 Built-in Alarm Sounds

| Sound | Description |
|---|---|
| ⚡ Neural Pulse | Ascending frequency burst |
| 🌧 Digital Rain | Matrix-style random digital droplets |
| 🌌 Cosmic Wake | Rising frequency space sweep |
| 🤖 Cyber Beep | Cyberpunk SOS urgent pattern |
| 🔔 Quantum Bell | Harmonic C-major overtone chime |

---

## 📁 Project Structure

```
AI-Alarm-System/
├── dist/            ← Contains the ready-to-use 'AI Alarm.exe' file
├── main.py          ← Source code (single file application)
├── alarms.json      ← Auto-created storage for your alarms and sleep data
├── requirements.txt ← Python dependencies for developers
└── README.md        ← You're reading this!
```

---

## 🛠️ Tech Stack

- **UI**: CustomTkinter (modern dark widgets)
- **Sound**: Pygame + NumPy (procedural sound generation)
- **AI Voice**: pyttsx3 (Text-to-Speech)
- **Voice Control**: SpeechRecognition + Google STT
- **Packaging**: PyInstaller

---

## 📸 Screenshots

> ![alt text](image-1.png)
> ![alt text](image.png)

---

## 🤝 Contributing

Pull requests welcome! Open an issue first to discuss changes.
