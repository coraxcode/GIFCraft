import tkinter as tk
from tkinter import filedialog, messagebox, Frame, Canvas, Menu, Checkbutton, IntVar, Scrollbar
from PIL import Image, ImageTk, ImageSequence
import os

class GIFEditor:
    def __init__(self, master):
        """Initialize the GIF editor with the main window and UI setup."""
        self.master = master
        self.master.title("GIFCraft - GIF Editor")
        self.master.geometry("800x600")

        # Initial settings
        self.frame_index = 0
        self.frames = []
        self.delays = []
        self.is_playing = False
        self.history = []
        self.redo_stack = []
        self.current_file = None
        self.checkbox_vars = []
        self.check_all = tk.BooleanVar(value=False)  # Variable to keep track of check/uncheck state

        # Setup UI and bindings
        self.setup_ui()
        self.bind_keyboard_events()

    def update_title(self):
        """Update the window title to reflect the current file state."""
        if self.frames:
            if self.current_file:
                self.master.title(f"GIFCraft - GIF Editor - {os.path.basename(self.current_file)}")
            else:
                self.master.title("GIFCraft - GIF Editor - Unsaved File")
        else:
            self.master.title("GIFCraft - GIF Editor")

    def setup_ui(self):
        """Set up the user interface."""
        self.setup_menu()
        self.setup_frame_list()
        self.setup_control_frame()

    def setup_menu(self):
        """Set up the menu bar."""
        self.menu_bar = Menu(self.master)
        self.create_file_menu()
        self.create_edit_menu()
        self.create_animation_menu()
        self.create_help_menu()  # Add this line to include the Help menu
        self.master.config(menu=self.menu_bar)

    def create_file_menu(self):
        """Create the File menu."""
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Load GIF/PNG/WebP", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Extract Frames", command=self.extract_frames)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

    def create_edit_menu(self):
        """Create the Edit menu."""
        edit_menu = Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Add Image", command=self.add_image)
        edit_menu.add_command(label="Delete Frame(s)", command=self.delete_frames, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Move Frame Up", command=self.move_frame_up, accelerator="Arrow Up")
        edit_menu.add_command(label="Move Frame Down", command=self.move_frame_down, accelerator="Arrow Down")
        edit_menu.add_separator()
        edit_menu.add_command(label="Check/Uncheck All", command=self.toggle_check_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

    def create_animation_menu(self):
        """Create the Animation menu."""
        animation_menu = Menu(self.menu_bar, tearoff=0)
        animation_menu.add_command(label="Play/Stop Animation", command=self.toggle_play_pause, accelerator="Space")
        self.menu_bar.add_cascade(label="Animation", menu=animation_menu)

    def create_help_menu(self):
        """Create the Help menu."""
        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)  # Add this line to create the About menu item
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def setup_frame_list(self):
        """Set up the frame list with scrollbar."""
        self.frame_list_frame = Frame(self.master)
        self.frame_list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = Scrollbar(self.frame_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = Canvas(self.frame_list_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)

        self.frame_list = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_list, anchor='nw')

    def setup_control_frame(self):
        """Set up the control frame with image display."""
        self.control_frame_canvas = Canvas(self.master)
        self.control_frame_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.control_frame_scrollbar = Scrollbar(self.control_frame_canvas, orient="vertical", command=self.control_frame_canvas.yview)
        self.control_frame_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.control_frame = Frame(self.control_frame_canvas)
        self.control_frame_canvas.create_window((0, 0), window=self.control_frame, anchor='nw')

        self.control_frame_canvas.config(yscrollcommand=self.control_frame_scrollbar.set)
        self.control_frame.bind("<Configure>", lambda e: self.control_frame_canvas.config(scrollregion=self.control_frame_canvas.bbox("all")))

        self.image_label = tk.Label(self.control_frame)
        self.image_label.pack()

        self.dimension_label = tk.Label(self.control_frame, text="", font=("Arial", 8), fg="grey")
        self.dimension_label.pack(pady=5)

        self.total_duration_label = tk.Label(self.control_frame, text="", font=("Arial", 8), fg="grey")
        self.total_duration_label.pack(pady=5)

        self.delay_label = tk.Label(self.control_frame, text="Frame Delay (ms):")
        self.delay_label.pack(pady=5)

        self.delay_entry = tk.Entry(self.control_frame)
        self.delay_entry.pack(pady=5)

        self.delay_button = tk.Button(self.control_frame, text="Set Frame Delay", command=self.set_delay)
        self.delay_button.pack(pady=5)

        # Play/Stop button with an indicator
        self.play_button = tk.Button(self.control_frame, text="Play", command=self.toggle_play_pause)
        self.play_button.pack(pady=5)

    def bind_keyboard_events(self):
        """Bind keyboard events for navigating frames."""
        self.master.bind("<Control-o>", self.load_file)
        self.master.bind("<Control-O>", self.load_file)
        self.master.bind("<Left>", self.previous_frame)
        self.master.bind("<Right>", self.next_frame)
        self.master.bind("<Up>", self.move_frame_up)
        self.master.bind("<Down>", self.move_frame_down)
        self.master.bind("<Delete>", self.delete_frames)
        self.master.bind("<space>", self.toggle_play_pause)
        self.master.bind("<Control-z>", self.undo)
        self.master.bind("<Control-Z>", self.undo)
        self.master.bind("<Control-y>", self.redo)
        self.master.bind("<Control-Y>", self.redo)
        self.master.bind("<Control-s>", self.save)
        self.master.bind("<Control-S>", self.save_as)
        self.master.bind("x", self.toggle_checkbox)
        self.master.bind("X", self.toggle_checkbox)

    def toggle_play_pause(self, event=None):
        """Toggle play/pause for the animation."""
        if self.is_playing:
            self.stop_animation()
        else:
            self.play_animation()

    def previous_frame(self, event=None):
        """Show the previous frame."""
        if self.frame_index > 0:
            self.frame_index -= 1
            self.show_frame()

    def next_frame(self, event=None):
        """Show the next frame."""
        if self.frame_index < len(self.frames) - 1:
            self.frame_index += 1
            self.show_frame()

    def load_file(self, event=None):
        """Load a GIF, PNG, or WebP file and extract its frames."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.gif *.png *.webp")])
        if not file_path:
            return

        self.save_state()  # Save the state before making changes
        self.frames = []
        self.delays = []
        self.checkbox_vars = []
        for widget in self.frame_list.winfo_children():
            widget.destroy()

        try:
            with Image.open(file_path) as img:
                for frame in ImageSequence.Iterator(img):
                    self.frames.append(self.center_image(self.resize_image(frame.copy())))
                    delay = int(frame.info.get('duration', 100))  # Ensure delay is always an integer
                    self.delays.append(delay)
                    var = IntVar()
                    var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
                    self.checkbox_vars.append(var)
            self.frame_index = 0
            self.update_frame_list()
            self.show_frame()
            self.current_file = file_path
            self.update_title()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def resize_image(self, image, max_width=800, max_height=600):
        """Resize the image to fit within the specified max width and height."""
        width, height = image.size
        if width > max_width or height > max_height:
            scaling_factor = min(max_width / width, max_height / height)
            new_size = (int(width * scaling_factor), int(height * scaling_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def center_image(self, image):
        """Center the image within the maximum frame size."""
        max_width = max((frame.width for frame in self.frames + [image]), default=image.width)
        max_height = max((frame.height for frame in self.frames + [image]), default=image.height)

        new_image = Image.new("RGBA", (max_width, max_height), (255, 255, 255, 0))
        new_image.paste(image, ((max_width - image.width) // 2, (max_height - image.height) // 2))

        return new_image

    def add_image(self):
        """Add images to the frames."""
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.gif *.bmp")])
        if not file_paths:
            return

        self.save_state()  # Save the state before making changes
        try:
            for file_path in file_paths:
                with Image.open(file_path) as image:
                    self.frames.append(self.center_image(self.resize_image(image.copy())))
                self.delays.append(100)  # Default delay for added images
                var = IntVar()
                var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
                self.checkbox_vars.append(var)
            self.update_frame_list()
            self.show_frame()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add images: {e}")

    def update_frame_list(self):
        """Update the listbox with the current frames and their delays."""
        for widget in self.frame_list.winfo_children():
            widget.destroy()

        for i, (delay, var) in enumerate(zip(self.delays, self.checkbox_vars)):
            frame = Frame(self.frame_list)
            frame.pack(fill=tk.X)
            checkbox = Checkbutton(frame, variable=var)
            checkbox.pack(side=tk.LEFT)
            
            # Add an arrow to indicate the current frame
            if i == self.frame_index:
                label = tk.Label(frame, text=f"→ Frame {i + 1}: {delay} ms")
            else:
                label = tk.Label(frame, text=f"Frame {i + 1}: {delay} ms")
            label.pack(side=tk.LEFT, fill=tk.X)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def set_current_frame(self, index):
        """Set the current frame to the one corresponding to the clicked checkbox."""
        self.frame_index = index
        self.show_frame()

    def show_frame(self):
        """Display the current frame."""
        if self.frames:
            frame = self.frames[self.frame_index]
            preview = self.resize_image(frame, max_width=800, max_height=600)
            photo = ImageTk.PhotoImage(preview)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.image_label.config(text='')  # Remove text when showing image
            self.delay_entry.delete(0, tk.END)
            self.delay_entry.insert(0, str(self.delays[self.frame_index]))
            self.dimension_label.config(text=f"Size: {frame.width}x{frame.height}")  # Show frame dimensions
            total_duration = sum(self.delays)
            self.total_duration_label.config(text=f"Total Duration: {total_duration} ms")  # Show total duration
        else:
            self.image_label.config(image='', text="No frames to display")
            self.image_label.image = None
            self.delay_entry.delete(0, tk.END)
            self.dimension_label.config(text="")  # Clear frame dimensions
            self.total_duration_label.config(text="")  # Clear total duration
        self.update_frame_list()  # Refresh the frame list to show the current frame indicator

    def delete_frames(self, event=None):
        """Delete the selected frames."""
        if not self.frames:
            messagebox.showerror("Error", "No frames to delete.")
            return

        self.save_state()  # Save the state before making changes
        indices_to_delete = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if not indices_to_delete:
            messagebox.showinfo("Info", "No frames selected for deletion.")
            return

        for index in reversed(indices_to_delete):
            del self.frames[index]
            del self.delays[index]
            del self.checkbox_vars[index]

        # Update frame_index to ensure it is within the correct bounds
        if self.frame_index >= len(self.frames):
            self.frame_index = max(0, len(self.frames) - 1)

        self.update_frame_list()
        self.show_frame()  # Update the frame display

    def move_frame_up(self, event=None):
        """Move the selected frames up in the list."""
        self.save_state()  # Save the state before making changes
        indices_to_move = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        for i in indices_to_move:
            if i > 0 and i-1 not in indices_to_move:
                self.frames[i], self.frames[i-1] = self.frames[i-1], self.frames[i]
                self.delays[i], self.delays[i-1] = self.delays[i-1], self.delays[i]
                self.checkbox_vars[i].set(0)
                self.checkbox_vars[i-1].set(1)
                if i == self.frame_index:
                    self.frame_index = i - 1
                elif i - 1 == self.frame_index:
                    self.frame_index = i

        self.update_frame_list()
        self.show_frame()  # Update the frame display

    def move_frame_down(self, event=None):
        """Move the selected frames down in the list."""
        self.save_state()  # Save the state before making changes
        indices_to_move = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        for i in reversed(indices_to_move):
            if i < len(self.frames) - 1 and i+1 not in indices_to_move:
                self.frames[i], self.frames[i+1] = self.frames[i+1], self.frames[i]
                self.delays[i], self.delays[i+1] = self.delays[i+1], self.delays[i]
                self.checkbox_vars[i].set(0)
                self.checkbox_vars[i+1].set(1)
                if i == self.frame_index:
                    self.frame_index = i + 1
                elif i + 1 == self.frame_index:
                    self.frame_index = i

        self.update_frame_list()
        self.show_frame()  # Update the frame display

    def play_animation(self):
        """Play the GIF animation."""
        self.is_playing = True
        self.play_button.config(text="Stop")
        self.play_next_frame()

    def stop_animation(self):
        """Stop the GIF animation."""
        self.is_playing = False
        self.play_button.config(text="Play")

    def play_next_frame(self):
        """Play the next frame in the animation."""
        if self.is_playing and self.frames:
            self.show_frame()
            delay = self.delays[self.frame_index]
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.master.after(delay, self.play_next_frame)

    def set_delay(self):
        """Set the delay for the selected frames."""
        try:
            delay = int(self.delay_entry.get())
            self.save_state()  # Save the state before making changes
            for i, var in enumerate(self.checkbox_vars):
                if var.get() == 1:
                    self.delays[i] = delay
            self.update_frame_list()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for delay.")

    def save(self, event=None):
        """Save the current frames and delays to a GIF file."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as()

    def save_as(self, event=None):
        """Save the current frames and delays to a file with the selected format."""
        file_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif"), ("PNG files", "*.png"), ("WebP files", "*.webp")])
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.update_title()

    def save_to_file(self, file_path):
        """Save the frames and delays to the specified file in the given format."""
        if self.frames:
            try:
                _, ext = os.path.splitext(file_path)
                ext = ext[1:].lower()  # Remove the dot and convert to lowercase
                if ext == 'gif':
                    self.frames[0].save(file_path, save_all=True, append_images=self.frames[1:], duration=self.delays, loop=0)
                elif ext == 'png':
                    self.frames[0].save(file_path, save_all=True, append_images=self.frames[1:], duration=self.delays, loop=0, format='PNG')
                elif ext == 'webp':
                    self.frames[0].save(file_path, save_all=True, append_images=self.frames[1:], duration=self.delays, loop=0, format='WEBP')
                else:
                    messagebox.showerror("Error", f"Unsupported file format: {ext.upper()}")
                    return
                self.current_file = file_path
                self.update_title()
                messagebox.showinfo("Success", f"{ext.upper()} saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save {ext.upper()}: {e}")

    def extract_frames(self):
        """Extract the frames and save them as individual images."""
        if not self.frames:
            messagebox.showerror("Error", "No frames to extract.")
            return

        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        try:
            for i, frame in enumerate(self.frames):
                frame_path = os.path.join(folder_path, f"frame_{i + 1}.png")
                frame.save(frame_path)
            messagebox.showinfo("Success", "Frames extracted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract frames: {e}")

    def save_state(self):
        """Save the current state for undo functionality."""
        self.history.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
        self.redo_stack.clear()  # Clear the redo stack on new action


    def undo(self, event=None):
        """Undo the last action."""
        if self.history:
            self.redo_stack.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
            self.frames, self.delays, checkbox_states, self.frame_index, self.current_file = self.history.pop()
            self.checkbox_vars = [IntVar(value=state) for state in checkbox_states]
            for i, var in enumerate(self.checkbox_vars):
                var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
            self.update_frame_list()
            self.show_frame()
            self.update_title()

    def redo(self, event=None):
        """Redo the last undone action."""
        if self.redo_stack:
            self.history.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
            self.frames, self.delays, checkbox_states, self.frame_index, self.current_file = self.redo_stack.pop()
            self.checkbox_vars = [IntVar(value=state) for state in checkbox_states]
            for i, var in enumerate(self.checkbox_vars):
                var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
            self.update_frame_list()
            self.show_frame()
            self.update_title()

    def toggle_check_all(self):
        """Toggle all checkboxes in the frame list."""
        self.save_state()  # Save the state before making changes
        new_state = not self.check_all.get()
        self.check_all.set(new_state)
        for var in self.checkbox_vars:
            var.set(1 if new_state else 0)
        self.update_frame_list()

    def toggle_checkbox(self, event=None):
        """Toggle the checkbox of the current frame."""
        if self.checkbox_vars:
            current_var = self.checkbox_vars[self.frame_index]
            current_var.set(0 if current_var.get() else 1)

    def show_about(self):
        """Display the About dialog."""
        messagebox.showinfo("About GIFCraft", "GIFCraft - GIF Editor\nVersion 1.0\n© 2024 by Seehrum")

def main():
    root = tk.Tk()
    app = GIFEditor(master=root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program interrupted with Ctrl+C")
        root.destroy()

if __name__ == "__main__":
    main()
