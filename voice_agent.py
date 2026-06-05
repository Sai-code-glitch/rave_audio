import os
import sys
import subprocess
import time
import speech_recognition as sr

PROJECT_DIR = "C:/Users/saija/Desktop/rave_audio"
COMPILER_SCRIPT = "C:/Users/saija/Desktop/build_and_push.py"

def run_matrix_pipeline():
    print("\n" + "="*50)
    print("🚀 MASTER TRIGGER ACTIVE: COMPILING ENTIRE CORE RAVE ARCHITECTURE")
    print("="*50)
    
    if not os.path.exists(COMPILER_SCRIPT):
        print(f"[✘] Structural Error: Compiler script not found at {COMPILER_SCRIPT}")
        return

    try:
        result = subprocess.run(
            [sys.executable, COMPILER_SCRIPT],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print("[✔] SUCCESS: All audio, visual, and code layers updated hands-free!")
    except subprocess.CalledProcessError as e:
        print(f"[✘] Compilation Error:\n{e.stderr}")

def master_voice_loop():
    recognizer = sr.Recognizer()
    
    # 🎛️ MASTER AMPLIFICATION CALIBRATION
    recognizer.dynamic_energy_threshold = False  # Lock threshold so it doesn't drift away
    recognizer.energy_threshold = 150            # High sensitivity floor for clear accent capture
    recognizer.pause_threshold = 0.5             # Fast snap capture immediately after you finish speaking
    recognizer.operation_timeout = 3             # Kill dead air hangs instantly

    print("\n==================================================")
    print("       RAVE ENGINE: MASTER VOICE CONTROLLER       ")
    print("==================================================")
    print("[-] Mapping high-sensitivity audio stream channels...")
    
    try:
        microphone = sr.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5) # Fast room noise snap
    except Exception as e:
        print(f"[✘] Hardware Access Fault: {e}")
        return

    print(f"[✔] MASTER CORES ACTIVE (Acoustic Gain Level: {recognizer.energy_threshold})")
    print("[▶] LISTENING ACTIVE... Say 'UPDATE PROJECT' or simply shout 'UPDATE'...")

    while True:
        try:
            with microphone as source:
                # Capture the tightest possible audio packet window
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
            
            print("\n[-] Decoding audio wave frequencies...", end="", flush=True)
            
            # Request high-speed phrase translation
            text_match = recognizer.recognize_google(audio).lower().strip()
            print(f"\r[🎤 Master Heard]: '{text_match}'")
            
            # Widen the acoustic net: any match triggers the build cascade immediately
            trigger_words = ["update", "project", "progress", "up", "date", "object"]
            if any(word in text_match for word in trigger_words):
                run_matrix_pipeline()
                
            print("\n[▶] Master Listener restored. Streaming...")

        except sr.UnknownValueError:
            # Print a subtle visual pulse so you know the hardware layer is actively tracking sound
            print("🎚️", end="", flush=True)
            continue
        except sr.RequestError:
            print("\n[!] Local network buffer lag detected. Recalibrating channels...")
            time.sleep(1)
            continue
        except KeyboardInterrupt:
            print("\n[-] Disengaging Master Daemon. Core offline.")
            break
        except Exception:
            continue

if __name__ == "__main__":
    master_voice_loop()