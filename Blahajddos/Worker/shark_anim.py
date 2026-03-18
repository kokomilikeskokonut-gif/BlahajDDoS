import os

import sys

import time

import subprocess

from PIL import Image


# --- AUTO-DEPENDENCY CHECK ---

try:

    import ascii_magic

except ImportError:

    print("[!] Missing libraries. Attempting auto-fix...")

    subprocess.call([sys.executable, "-m", "pip", "install", "pillow", "ascii_magic"])

    import ascii_magic


# --- CONFIGURATION ---

PROJECT_DIR = r"%USERPROFILE%\Downloads\BlahajDDoS-main\BlahajDDoS-main\Blahajddos\Worker"

GIF_PATH = os.path.join(PROJECT_DIR, "ascii-animation.gif")


# ANSI Colors

LIGHT_BLUE = "\033[94m"

RESET = "\033[0m"


def run_infinite_gif(path, columns=100, speed=0.06):

    """Pre-processes the GIF and plays it on an infinite loop in light blue."""

    if not os.path.exists(path):

        print(f"[!] GIF not found at {path}")

        return

    

    try:

        img = Image.open(path)

        frames_ansi = []

        num_frames = getattr(img, 'n_frames', 1)

        

        print(f"[*] Pre-processing {num_frames} frames...")

        

        for i in range(num_frames):

            img.seek(i)

            frame_rgb = img.convert("RGB")

            temp_frame = f"temp_loop_{i}.png"

            frame_rgb.save(temp_frame)

            

            # Convert to ASCII. Note: We strip existing colors to apply our own.

            art = ascii_magic.from_image(temp_frame)

            # We get the raw string to wrap it in our LIGHT_BLUE code

            frames_ansi.append(art.to_ascii(columns=columns))

            

            if os.path.exists(temp_frame):

                os.remove(temp_frame)


        # Initialize Terminal

        if os.name == 'nt':

            os.system('cls')

            os.system('') # Enable ANSI support for Windows CMD/PowerShell

        else:

            os.system('clear')


        # --- INFINITE LOOP ---

        try:

            while True:

                for frame in frames_ansi:

                    # \033[H moves cursor to top-left

                    # We wrap the frame in LIGHT_BLUE and RESET

                    sys.stdout.write("\033[H" + LIGHT_BLUE + frame + RESET) 

                    sys.stdout.flush()

                    time.sleep(speed)

        except KeyboardInterrupt:

            if os.name == 'nt': os.system('cls')

            else: os.system('clear')

            print(f"\n{LIGHT_BLUE}[+] Animation stopped.{RESET}")


    except Exception as e:

        print(f"\n[!] Error: {e}")


def main():

    # Adjust columns for width and speed for frame rate

    run_infinite_gif(GIF_PATH, columns=100, speed=0.05)


if __name__ == "__main__":

    main() 
