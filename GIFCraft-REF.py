import tkinter as tk
from tkinter import filedialog, messagebox, Frame, Canvas, Menu, Checkbutton, IntVar, Scrollbar, simpledialog
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
        self.check_all = tk.BooleanVar(value=False)

        # Setup UI and bindings
        self.setup_ui()
        self.bind_keyboard_events()

    def update_title(self):
        """Update the window title to reflect the current file state."""
        if self.frames:
            title = f"GIFCraft - GIF Editor - {os.path.basename(self.current_file)}" if self.current_file else "GIFCraft - GIF Editor - Unsaved File"
            self.master.title(title)
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
        self.create_help_menu()
        self.master.config(menu=self.menu_bar)

    def create_file_menu(self):
        """Create the File menu."""
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Load GIF/PNG/WebP", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As High Quality GIF", command=self.save_as_high_quality_gif)
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
        edit_menu.add_command(label="Check/Uncheck All", command=self.toggle_check_all, accelerator="A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Resize Frames", command=self.resize_frames_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_frames, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_frames, accelerator="Ctrl+V")
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
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def new_file(self, event=None):
        """Create a new file, prompting to save unsaved changes if any."""
        if self.frames:
            response = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save the current file before creating a new one?")
            if response:  # Yes
                self.save()
                if self.frames:  # If saving was cancelled or failed, do not proceed
                    return
            elif response is None:  # Cancel
                return

        # Reset the editor state for a new file
        self.frames = []
        self.delays = []
        self.checkbox_vars = []
        self.current_file = None
        self.frame_index = 0
        self.base_size = None  # Clear the base size
        self.update_frame_list()
        self.show_frame()
        self.update_title()

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
                for i, frame in enumerate(ImageSequence.Iterator(img)):
                    if i == 0:
                        self.base_size = frame.size  # Store the size of the first frame
                    self.frames.append(self.resize_to_base_size(frame.copy()))
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

    def save_as_high_quality_gif(self):
        """Save the current frames and delays to a high-quality GIF file using dithering."""
        file_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
        if file_path:
            try:
                images = [frame.convert("RGB").quantize(method=0) for frame in self.frames]
                images[0].save(file_path, save_all=True, append_images=images[1:], duration=self.delays, loop=0, dither=Image.NONE)
                self.current_file = file_path
                self.update_title()
                messagebox.showinfo("Success", "High-quality GIF saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save high-quality GIF: {e}")

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

    def add_image(self):
        """Add images to the frames."""
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.gif *.bmp")])
        if not file_paths:
            return

        self.save_state()  # Save the state before making changes
        try:
            for file_path in file_paths:
                with Image.open(file_path) as image:
                    # Resize the new image to match the base dimensions
                    if not self.frames:  # If no frames, set the base size to the first image's size
                        self.base_size = image.size
                    image = self.resize_to_base_size(image.copy())
                    self.frames.append(image)
                self.delays.append(100)  # Default delay for added images
                var = IntVar()
                var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
                self.checkbox_vars.append(var)

            self.update_frame_list()
            self.show_frame()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add images: {e}")

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
        """Move the selected frame up in the list."""
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if len(selected_indices) != 1:
            messagebox.showwarning("Selection Error", "Please select exactly one frame to move.")
            return

        selected_index = selected_indices[0]

        if selected_index == 0:
            messagebox.showinfo("Move Up", "The selected frame is already at the top.")
            return

        self.save_state()  # Save the state before making changes

        # Swap the frames and delays
        self.frames[selected_index], self.frames[selected_index - 1] = self.frames[selected_index - 1], self.frames[selected_index]
        self.delays[selected_index], self.delays[selected_index - 1] = self.delays[selected_index - 1], self.delays[selected_index]

        # Move the check state
        self.checkbox_vars[selected_index].set(0)
        self.checkbox_vars[selected_index - 1].set(1)

        # Update the frame index to the new position of the moved frame
        self.frame_index = selected_index - 1

        self.update_frame_list()
        self.show_frame()

    def move_frame_down(self, event=None):
        """Move the selected frame down in the list."""
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if len(selected_indices) != 1:
            messagebox.showwarning("Selection Error", "Please select exactly one frame to move.")
            return

        selected_index = selected_indices[0]

        if selected_index == len(self.frames) - 1:
            messagebox.showinfo("Move Down", "The selected frame is already at the bottom.")
            return

        self.save_state()  # Save the state before making changes

        # Swap the frames and delays
        self.frames[selected_index], self.frames[selected_index + 1] = self.frames[selected_index + 1], self.frames[selected_index]
        self.delays[selected_index], self.delays[selected_index + 1] = self.delays[selected_index + 1], self.delays[selected_index]

        # Move the check state
        self.checkbox_vars[selected_index].set(0)
        self.checkbox_vars[selected_index + 1].set(1)

        # Update the frame index to the new position of the moved frame
        self.frame_index = selected_index + 1

        self.update_frame_list()
        self.show_frame()

    def resize_frames_dialog(self):
        """Open a simple dialog to get new size and resize all frames."""
        if not any(var.get() for var in self.checkbox_vars):
            messagebox.showinfo("info", "No frames are selected for resizing.")
            return

        width = simpledialog.askinteger("Input", "Enter new width:", parent=self.master, minvalue=1)
        height = simpledialog.askinteger("Input", "Enter new height:", parent=self.master, minvalue=1)
        
        if width and height:
            self.resize_frames(width, height)

    def resize_frames(self, new_width, new_height):
        """Resize all checked frames to the specified width and height."""
        self.save_state()
        for i, frame in enumerate(self.frames):
            if self.checkbox_vars[i].get():
                self.frames[i] = frame.resize((new_width, new_height), Image.LANCZOS)
        self.update_frame_list()
        self.show_frame()

    def copy_frames(self, event=None):
        """Copy the selected frames to the clipboard."""
        self.copied_frames = [(self.frames[i].copy(), self.delays[i]) for i in range(len(self.checkbox_vars)) if self.checkbox_vars[i].get() == 1]
        if not self.copied_frames:
            messagebox.showinfo("Info", "No frames selected to copy.")
        else:
            messagebox.showinfo("Info", f"Copied {len(self.copied_frames)} frame(s).")

    def paste_frames(self, event=None):
        """Paste the copied frames below the selected frames with all checkboxes checked."""
        # Check if there are any frames copied
        if not hasattr(self, 'copied_frames') or not self.copied_frames:
            messagebox.showerror("Error", "No frames to paste. Please copy frames first.")
            return

        # Get the selected indices
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        if not selected_indices:
            messagebox.showinfo("Info", "No frames selected to paste after. Pasting at the end.")
            insert_index = len(self.frames)
        else:
            insert_index = max(selected_indices) + 1

        # Save the current state for undo functionality
        self.save_state()

        # Insert the copied frames and delays at the specified index
        for frame, delay in self.copied_frames:
            self.frames.insert(insert_index, frame)
            self.delays.insert(insert_index, delay)
            var = IntVar(value=1)  # Set the checkbox to be checked by default
            var.trace_add('write', lambda *args, i=insert_index: self.set_current_frame(i))
            self.checkbox_vars.insert(insert_index, var)
            insert_index += 1

        # Update the frame list and display the current frame
        self.update_frame_list()
        self.show_frame()

    def undo(self, event=None):
        """Undo the last action."""
        if self.history:
            self.redo_stack.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
            self.frames, self.delays, checkbox_states, self.frame_index, self.current_file = self.history.pop()
            self.checkbox_vars = [IntVar(value=state) for state in checkbox_states]
            for i, var in enumerate(self.checkbox_vars):
                var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
            self.base_size = self.frames[0].size if self.frames else None  # Reset base size based on the remaining frames
            self.update_frame_list()
            self.show_frame()
            self.update_title()
            self.check_all.set(False)  # Reset the check_all variable to ensure consistency

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
            self.check_all.set(False)  # Reset the check_all variable to ensure consistency

    def toggle_check_all(self, event=None):
        """Toggle all checkboxes in the frame list without scrolling or changing the displayed frame."""
        self.save_state()  # Save the state before making changes
        new_state = not self.check_all.get()
        self.check_all.set(new_state)
        
        # Temporarily remove traces
        for var in self.checkbox_vars:
            var.trace_remove('write', var.trace_info()[0][1])
        
        for var in self.checkbox_vars:
            var.set(1 if new_state else 0)
        
        # Re-add traces
        for i, var in enumerate(self.checkbox_vars):
            var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
        
        self.update_frame_list()

    def toggle_play_pause(self, event=None):
        """Toggle play/pause for the animation."""
        if self.is_playing:
            self.stop_animation()
        else:
            self.play_animation()

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

    def set_delay(self, event=None):
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

    def focus_delay_entry(self, event=None):
        """Set focus to the delay entry field and scroll to the current frame."""
        self.delay_entry.focus_set()
        self.focus_current_frame()
    
    def focus_current_frame(self):
        """Ensure the current frame is visible in the frame list."""
        if self.frame_list.winfo_children():
            frame_widgets = self.frame_list.winfo_children()
            current_frame_widget = frame_widgets[self.frame_index]
            self.canvas.yview_moveto(current_frame_widget.winfo_y() / self.canvas.bbox("all")[3])

    def show_about(self):
        """Display the About dialog."""
        messagebox.showinfo("About GIFCraft", "GIFCraft - GIF Editor\nVersion 1.0\n© 2024 by Seehrum")

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
        self.control_frame_canvas = tk.Canvas(self.master)
        self.control_frame_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.control_frame_scrollbar = Scrollbar(self.control_frame_canvas, orient="vertical", command=self.control_frame_canvas.yview)
        self.control_frame_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.control_frame = tk.Frame(self.control_frame_canvas)
        self.control_frame_canvas.create_window((0, 0), window=self.control_frame, anchor='nw')

        self.control_frame_canvas.config(yscrollcommand=self.control_frame_scrollbar.set)
        self.control_frame.bind("<Configure>", lambda e: self.control_frame_canvas.config(scrollregion=self.control_frame_canvas.bbox("all")))

        # Frame for image display
        self.image_display_frame = tk.Frame(self.control_frame)
        self.image_display_frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')

        self.image_label = tk.Label(self.image_display_frame)
        self.image_label.pack()

        self.dimension_label = tk.Label(self.image_display_frame, text="", font=("Arial", 8), fg="grey")
        self.dimension_label.pack(pady=5)

        self.total_duration_label = tk.Label(self.image_display_frame, text="", font=("Arial", 8), fg="grey")
        self.total_duration_label.pack(pady=5)

        # Frame for control inputs
        self.control_inputs_frame = tk.Frame(self.control_frame)
        self.control_inputs_frame.grid(row=1, column=0, padx=20, pady=10, sticky='n')

        self.delay_label = tk.Label(self.control_inputs_frame, text="Frame Delay (ms):")
        self.delay_label.grid(row=0, column=0, pady=5, sticky=tk.E)

        vcmd = (self.master.register(self.validate_delay), '%P')
        self.delay_entry = tk.Entry(self.control_inputs_frame, validate='key', validatecommand=vcmd)
        self.delay_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)

        self.delay_button = tk.Button(self.control_inputs_frame, text="Set Frame Delay", command=self.set_delay)
        self.delay_button.grid(row=1, column=0, columnspan=2, pady=5)

        self.play_button = tk.Button(self.control_inputs_frame, text="Play", command=self.toggle_play_pause)
        self.play_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Make sure the window is scrolled to the correct size
        self.control_frame.update_idletasks()
        self.control_frame_canvas.config(scrollregion=self.control_frame.bbox("all"))

    def validate_delay(self, new_value):
        """Validate that the delay entry contains only digits."""
        if new_value.isdigit() or new_value == "":
            return True
        else:
            return False

    def bind_keyboard_events(self):
        """Bind keyboard events for navigating frames."""
        self.delay_entry.bind("<Return>", self.set_delay)
        self.master.bind("<Control-n>", self.new_file)
        self.master.bind("<Control-N>", self.new_file)
        self.master.bind("<Control-o>", self.load_file)
        self.master.bind("<Control-O>", self.load_file)
        self.master.bind("<Left>", self.previous_frame)
        self.master.bind("<Right>", self.next_frame)
        self.master.bind("<Up>", self.move_frame_up)
        self.master.bind("<Down>", self.move_frame_down)
        self.master.bind("<Delete>", self.delete_frames)
        self.master.bind("<space>", self.toggle_play_pause)
        self.master.bind("<Control-c>", self.copy_frames)
        self.master.bind("<Control-C>", self.copy_frames)
        self.master.bind("<Control-v>", self.paste_frames)
        self.master.bind("<Control-V>", self.paste_frames)
        self.master.bind("<Control-z>", self.undo)
        self.master.bind("<Control-Z>", self.undo)
        self.master.bind("<Control-y>", self.redo)
        self.master.bind("<Control-Y>", self.redo)
        self.master.bind("<Control-s>", self.save)
        self.master.bind("<Control-S>", self.save_as)
        self.master.bind("x", self.toggle_checkbox)
        self.master.bind("X", self.toggle_checkbox)
        self.master.bind("a", self.toggle_check_all)
        self.master.bind("A", self.toggle_check_all)
        self.master.bind("d", self.focus_delay_entry)
        self.master.bind("D", self.focus_delay_entry)

    def toggle_checkbox(self, event=None):
        """Toggle the checkbox of the current frame."""
        if self.checkbox_vars:
            current_var = self.checkbox_vars[self.frame_index]
            current_var.set(0 if current_var.get() else 1)

    def previous_frame(self, event=None):
        """Show the previous frame without altering the scrollbar position."""
        if self.frame_index > 0:
            self.frame_index -= 1
            self.show_frame()

    def next_frame(self, event=None):
        """Show the next frame without altering the scrollbar position."""
        if self.frame_index < len(self.frames) - 1:
            self.frame_index += 1
            self.show_frame()

    def resize_to_base_size(self, image):
        """Resize the image to the base size of the first frame and center it."""
        if hasattr(self, 'base_size'):
            base_width, base_height = self.base_size
            new_image = Image.new("RGBA", self.base_size, (0, 0, 0, 0))
            image = image.resize(self.base_size, Image.Resampling.LANCZOS)
            new_image.paste(image, ((base_width - image.width) // 2, (base_height - image.height) // 2))
            return new_image
        return image

    def update_frame_list(self):
        """Update the frame list with the current frames and their delays."""
        # Clear existing widgets
        for widget in self.frame_list.winfo_children():
            widget.destroy()

        # Display message if no frames are available
        if not self.frames:
            tk.Label(self.frame_list, text="No frames available").pack()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            return

        # Create and populate frame widgets
        for i, (frame, delay, var) in enumerate(zip(self.frames, self.delays, self.checkbox_vars)):
            frame_container = Frame(self.frame_list)
            frame_container.pack(fill=tk.X)

            checkbox = Checkbutton(frame_container, variable=var)
            checkbox.pack(side=tk.LEFT)

            frame_label_text = f"Frame {i + 1}: {delay} ms"
            if i == self.frame_index:
                frame_label_text = f"→ {frame_label_text}"

            label = tk.Label(frame_container, text=frame_label_text)
            label.pack(side=tk.LEFT, fill=tk.X)

        # Update the scroll region
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

    def save_state(self):
        """Save the current state for undo functionality."""
        self.history.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
        self.redo_stack.clear()  # Clear the redo stack on new action

    def resize_image(self, image, max_width, max_height):
        """Resize image while maintaining aspect ratio."""
        ratio = min(max_width / image.width, max_height / image.height)
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def main():
    """Main function to initialize the GIF editor."""
    root = tk.Tk()
    app = GIFEditor(master=root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program interrupted with Ctrl+C")
        root.destroy()


if __name__ == "__main__":
    main()
