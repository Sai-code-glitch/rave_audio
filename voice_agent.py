import os
import sys
import subprocess
import time
import speech_recognition as sr

PROJECT_DIR = "C:/Users/saija/Desktop/rave_audio"
COMPILER_SCRIPT = "C:/Users/saija/Desktop/build_and_push.py"

def run_matrix_pipeline():
    print("\n" + "="*50)
    print("🚀 MASTER TRIGGER: COMPILING ENTIRE CORE RAVE ARCHITECTURE")
    print("="*50)
    if not os.path.exists(COMPILER_SCRIPT):
        return
    try:
        result = subprocess.run([sys.executable, COMPILER_SCRIPT], capture_output=True, text=True, check=True)
        print("[OK] Master build compilation successfully synchronized.")
    except Exception as e:
        print(f"[✘] Error running compiler script: {e}")

def master_voice_loop():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = 150
    recognizer.pause_threshold = 0.5

    print("\n==================================================")
    print("       RAVE ENGINE: MASTER VOICE CONTROLLER       ")
    print("==================================================")
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

    print("[✔] MASTER CORES ACTIVE & STREAMING CHANNELS...")
    print("[▶] Say 'UPDATE PROJECT' or 'ENGAGE OVERDRIVE'...")

    while True:
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
            
            text_match = recognizer.recognize_google(audio).lower().strip()
            print(f"\r[🎤 Master Heard]: '{text_match}'")
            
            if "update" in text_match or "project" in text_match:
                run_matrix_pipeline()
            elif "engage" in text_match or "overdrive" in text_match:
                print("\n[⚡ OVERDRIVE CODE MATCHED] Injecting maximum voltage theme configurations...")
                # Run compiler to lock code, then pass instructions
                run_matrix_pipeline()
                
            print("\n[▶] Master Listener restored. Streaming...")
        except Exception:
            continue

if __name__ == "__main__":
    master_voice_loop()