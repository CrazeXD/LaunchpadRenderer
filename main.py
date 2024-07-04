import tkinter as tk
from tkinter import filedialog
import itertools
import launchpad_py as launchpad
import time
import os
from PIL import Image, ImageTk
import threading

class App:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.lp = launchpad.LaunchpadPro()
        print(self.lp.Open(0, "pad pro"))
        print(self.lp.Check())
        self.lp.ButtonFlush()
        self.lp.Reset()

    def setup_ui(self):
        self.root.title("GIF to Launchpad Renderer")
        self.root.geometry("960x540")

        # Use PanedWindow for layout
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left frame for controls
        self.control_frame = tk.Frame(self.paned_window, width=480, height=540)
        self.control_frame.pack_propagate(False)  # Prevents frame from shrinking
        self.paned_window.add(self.control_frame)

        # Styling controls
        self.title = tk.Label(self.control_frame, text="GIF to Launchpad Renderer", font=("Calibri", 24))
        self.title.pack(pady=10)
        self.path_label = tk.Label(self.control_frame, text="No file selected", font=("Calibri", 12))
        if self.path_label.cget('text') == "No file selected":
            self.path_label.config(fg="red")
        self.path_label.pack(pady=10)

        self.browse_button = tk.Button(self.control_frame, text="Browse", command=self.browse_file, font=("Calibri", 10), width=10)
        self.browse_button.pack(pady=5)

        self.start_button = tk.Button(self.control_frame, text="Start Rendering", command=self.start_rendering, font=("Calibri", 12), width=15)
        self.start_button.pack(pady=5)

        # Right frame for image display
        self.image_frame = tk.Frame(self.paned_window, width=480, height=540)
        self.image_frame.pack_propagate(False)  # Prevents frame from shrinking
        self.paned_window.add(self.image_frame)

        # Placeholder for image label
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(expand=True)

        # Load and display an initial image (placeholder or logo)
        self.display_image("novation-launchpad-pro-xl.jpg")

    def display_image(self, image_path):
        # Load the image with PIL
        pil_image = Image.open(image_path)
        pil_image = pil_image.resize((600, 458), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(pil_image)

        # Display the image in the label
        self.image_label.config(image=self.tk_image)

    # Existing methods (browse_file, start_rendering) remain unchanged

    def browse_file(self):
        if file_path := filedialog.askopenfilename(
            filetypes=[("GIF files", "*.gif")]
        ):
            self.path_label.config(text=file_path)
            self.file_path = file_path

    def start_rendering(self):
        if hasattr(self, 'file_path'):
            threading.Thread(target=self.render, args=(self.file_path,)).start()
        else:
            self.path_label.config(text="Please select a file first.")

    def render(self, gif):
        gifpath = os.path.dirname(gif)
        frames_dir = os.path.join(gifpath, 'frames')
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)
        self.extract_frames(gif, frames_dir)
        frames = os.listdir(frames_dir)
        for frame in frames:
            img = Image.open(os.path.join(frames_dir, frame))
            img = img.resize((8, 8))
            img = img.convert('RGB')
            for x, y in itertools.product(range(8), range(1, 9)):
                r, g, b = img.getpixel((x, y-1))
                self.lp.LedCtrlXYByRGB(x, y, [r, g, b])
            time.sleep(0.1)

    def extract_frames(self, inGif, outFolder):
        frame = Image.open(inGif)
        nframes = 0
        while frame:
            frame.save(f'{outFolder}/{os.path.basename(inGif)}-{nframes}.gif', 'GIF')
            nframes += 1
            try:
                frame.seek(nframes)
            except EOFError:
                break

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()