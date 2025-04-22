import numpy as np
import soundfile as sf
import tkinter as tk
import sounddevice as sd
from tkinter import messagebox

SAMPLE_RATE = 44100

def generate_binaural(left_freq, right_freq, hours, minutes, seconds, fade, volume, file_format):
    duration = hours * 3600 + minutes * 60 + seconds
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    left = volume * np.sin(2 * np.pi * left_freq * t)
    right = volume * np.sin(2 * np.pi * right_freq * t)

    if fade:
        fade_samples = int(SAMPLE_RATE * 0.1)
        fade_curve = np.linspace(0, 1, fade_samples)
        fade_out = fade_curve[::-1]

        left[:fade_samples] *= fade_curve
        right[:fade_samples] *= fade_curve
        left[-fade_samples:] *= fade_out
        right[-fade_samples:] *= fade_out

    stereo = np.stack([left, right], axis=1)
    fade_str = "_fade" if fade else ""
    filename = f"{int(left_freq)}_{int(right_freq)}_{hours:01d}h{minutes:02d}m{seconds:02d}s_vol{int(volume*100):03d}{fade_str}.{file_format}"
    sf.write(filename, stereo, SAMPLE_RATE, format=file_format.upper())
    return filename
    
def test_binaural_preview(left_freq, right_freq, volume, fade):
    duration = 3  # seconds
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    left = volume * np.sin(2 * np.pi * left_freq * t)
    right = volume * np.sin(2 * np.pi * right_freq * t)

    if fade:
        fade_samples = int(sr * 0.1)
        fade_curve = np.linspace(0, 1, fade_samples)
        fade_out = fade_curve[::-1]
        for wave in [left, right]:
            wave[:fade_samples] *= fade_curve
            wave[-fade_samples:] *= fade_out

    stereo = np.stack([left, right], axis=-1)
    sd.play(stereo, sr)

def run_gui():
    def test():
        try:
            left = float(entry_left.get())
            right = float(entry_right.get())
            vol = float(entry_volume.get())
            fade = fade_var.get()
            test_binaural_preview(left, right, vol, fade)
        except ValueError:
            messagebox.showerror("Error", "Invalid frequency or volume.")

    def on_generate():
        try:
            left = float(entry_left.get())
            right = float(entry_right.get())
            hrs = int(entry_hours.get())
            mins = int(entry_minutes.get())
            secs = int(entry_seconds.get())
            fade = fade_var.get()
            file_format = format_var.get()
            vol = float(entry_volume.get())
            filename = generate_binaural(left, right, hrs, mins, secs, fade, vol, file_format)
            messagebox.showinfo("Success", f"Saved as:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_diff_label(*args):
        try:
            left = float(entry_left.get())
            right = float(entry_right.get())
            diff = abs(left - right)
            diff_label.config(text=f"Δ = {diff:.2f} Hz (binaural beat)")
        except:
            diff_label.config(text="Δ = ? Hz")

    root = tk.Tk()
    root.title("Binaural Generator")
    
    currentRow = 0
    
    tk.Label(root, text="Left Frequency (Hz):").grid(row=currentRow, column=0, sticky='e')
    entry_left = tk.Entry(root)
    entry_left.insert(0, "178")
    entry_left.grid(row=currentRow, column=1)

    currentRow += 1
    tk.Label(root, text="Right Frequency (Hz):").grid(row=currentRow, column=0, sticky='e')
    entry_right = tk.Entry(root)
    entry_right.insert(0, "175")
    entry_right.grid(row=currentRow, column=1)

    currentRow += 1
    tk.Label(root, text="Δ = 3.00 Hz (binaural beat)").grid(row=currentRow, column=1, padx=10)

    currentRow += 1
    tk.Label(root, text="Hours:").grid(row=currentRow, column=0, sticky='e')
    entry_hours = tk.Entry(root)
    entry_hours.insert(0, "0")
    entry_hours.grid(row=currentRow, column=1)

    currentRow += 1
    tk.Label(root, text="Minutes:").grid(row=currentRow, column=0, sticky='e')
    entry_minutes = tk.Entry(root)
    entry_minutes.insert(0, "1")
    entry_minutes.grid(row=currentRow, column=1)

    currentRow += 1
    tk.Label(root, text="Seconds:").grid(row=currentRow, column=0, sticky='e')
    entry_seconds = tk.Entry(root)
    entry_seconds.insert(0, "0")
    entry_seconds.grid(row=currentRow, column=1)

    currentRow += 1
    tk.Label(root, text="Volume (0.0 to 1.0):").grid(row=currentRow, column=0)
    entry_volume = tk.Entry(root)
    entry_volume.insert(0, "0.5")
    entry_volume.grid(row=currentRow, column=1)
    
    currentRow += 1
    fade_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Fade In/Out (0.1s)", variable=fade_var).grid(row=currentRow, columnspan=2)

    currentRow += 1
    tk.Label(root, text="Format:").grid(row=currentRow, column=0, sticky='e')
    format_var = tk.StringVar(value="wav")

    currentRow += 1
    tk.Radiobutton(root, text="WAV", variable=format_var, value="wav").grid(row=currentRow, column=1, sticky="w")
    currentRow += 1
    tk.Radiobutton(root, text="FLAC", variable=format_var, value="flac").grid(row=currentRow, column=1, sticky="w")
    currentRow += 1
    tk.Radiobutton(root, text="MP3", variable=format_var, value="mp3").grid(row=currentRow, column=1, sticky="w")

    currentRow += 1
    tk.Button(root, text="Generate", command=on_generate).grid(row=currentRow, column=0, padx=5, pady=10)
    tk.Button(root, text="Test", command=test).grid(row=currentRow, column=1, padx=5, pady=10)

    entry_left.bind("<KeyRelease>", update_diff_label)
    entry_right.bind("<KeyRelease>", update_diff_label)


    root.mainloop()

run_gui()
