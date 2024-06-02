import tkinter as tk
from tkinter import filedialog, messagebox, Menu, Checkbutton, IntVar, Scrollbar, simpledialog
from PIL import Image, ImageTk, ImageSequence, ImageOps
import os

class GIFEditor:
    def __init__(self, master):
        """Initialize the GIF editor with the main window and UI setup."""
        self.master = master
        self.master.title("GIFCraft - GIF Editor")
        self.master.geometry("800x600")

        self.frame_index = 0
        self.frames = []
        self.delays = []
        self.is_playing = False
        self.history = []
        self.redo_stack = []
        self.current_file = None
        self.checkbox_vars = []
        self.check_all = tk.BooleanVar(value=False)

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
        self.create_effects_menu()
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
        edit_menu.add_command(label="Add Empty Frame", command=self.add_empty_frame)
        edit_menu.add_command(label="Delete Frame(s)", command=self.delete_frames, accelerator="Del")
        edit_menu.add_separator()        
        edit_menu.add_command(label="Move to Position", command=self.move_frames_to_position)
        edit_menu.add_command(label="Move Frame Up", command=self.move_frame_up, accelerator="Arrow Up")
        edit_menu.add_command(label="Move Frame Down", command=self.move_frame_down, accelerator="Arrow Down")
        edit_menu.add_separator()
        edit_menu.add_command(label="Check/Uncheck All", command=self.toggle_check_all, accelerator="A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Resize All Frames", command=self.resize_all_frames_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_frames, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_frames, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")    
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
    
    def create_effects_menu(self):
        """Create the Effects menu."""
        effects_menu = Menu(self.menu_bar, tearoff=0)
        effects_menu.add_command(label="Apply Crossfade Effect", command=self.apply_crossfade_effect)
        effects_menu.add_command(label="Desaturate Frames", command=self.desaturate_frames)
        effects_menu.add_command(label="Invert Colors", command=self.invert_colors_frames_dialog)
        effects_menu.add_command(label="Apply Tint Effect", command=self.apply_tint)
        effects_menu.add_command(label="Apply Sepia Effect", command=self.apply_sepia_effect_dialog)
        effects_menu.add_command(label="Reverse Frames", command=self.reverse_frames)        
        effects_menu.add_command(label="Crop Frames", command=self.crop_frames_dialog)
        effects_menu.add_command(label="Rotate Frames", command=self.rotate_frames_dialog)
        self.menu_bar.add_cascade(label="Effects", menu=effects_menu)

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

    def setup_frame_list(self):
        """Set up the frame list with scrollbar."""
        self.frame_list_frame = tk.Frame(self.master)
        self.frame_list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = Scrollbar(self.frame_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(self.frame_list_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)

        self.frame_list = tk.Frame(self.canvas)
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
        self.master.bind("<Control-S>", self.save)        
        self.master.bind("a", self.toggle_check_all)
        self.master.bind("A", self.toggle_check_all)
        self.master.bind("d", self.focus_delay_entry)
        self.master.bind("D", self.focus_delay_entry)
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
            self.show_frame(scroll=False)

    def next_frame(self, event=None):
        """Show the next frame."""
        if self.frame_index < len(self.frames) - 1:
            self.frame_index += 1
            self.show_frame(scroll=False)

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

        self.reset_editor_state()

    def load_file(self, event=None):
        """Load a GIF, PNG, or WebP file and extract its frames."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.gif *.png *.webp")])
        if not file_path:
            return

        self.save_state()  # Save the state before making changes
        self.reset_frames_and_vars()

        try:
            with Image.open(file_path) as img:
                for i, frame in enumerate(ImageSequence.Iterator(img)):
                    if i == 0:
                        self.base_size = frame.size
                    self.frames.append(self.resize_to_base_size(frame.copy()))
                    delay = int(frame.info.get('duration', 100))
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

    def resize_to_base_size(self, image):
        """Resize the image to the base size of the first frame and center it."""
        if hasattr(self, 'base_size'):
            base_width, base_height = self.base_size
            new_image = Image.new("RGBA", self.base_size, (0, 0, 0, 0))
            image = image.resize(self.base_size, Image.Resampling.LANCZOS)
            new_image.paste(image, ((base_width - image.width) // 2, (base_height - image.height) // 2))
            return new_image
        return image

    def resize_all_frames_dialog(self):
        """Open a dialog to get the new size and resize all frames."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Resize All Frames")

        tk.Label(dialog, text="New Width:").pack(pady=5)
        width_entry = tk.Entry(dialog)
        width_entry.pack(pady=5)

        tk.Label(dialog, text="New Height:").pack(pady=5)
        height_entry = tk.Entry(dialog)
        height_entry.pack(pady=5)

        def resize():
            try:
                new_width = int(width_entry.get())
                new_height = int(height_entry.get())
                self.resize_all_frames(new_width, new_height)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid integers for width and height.")

        tk.Button(dialog, text="Resize", command=resize).pack(pady=10)
        dialog.grab_set()

    def resize_all_frames(self, new_width=None, new_height=None):
        """Resize all frames to the specified width and height."""
        if new_width is None or new_height is None:
            if hasattr(self, 'base_size'):
                new_width, new_height = self.base_size
            else:
                return

        self.save_state()  # Save the state before making changes
        for i, frame in enumerate(self.frames):
            self.frames[i] = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.show_frame()
        self.update_frame_list()

    def resize_image(self, image, max_width=800, max_height=600):
        """Resize the image to fit within the specified max width and height."""
        width, height = image.size
        if width > max_width or height > max_height:
            scaling_factor = min(max_width / width, max_height / height)
            new_size = (int(width * scaling_factor), int(height * scaling_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def add_image(self):
        """Add images to the frames."""
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.gif *.bmp")])
        if not file_paths:
            return

        self.save_state()  # Save the state before making changes
        try:
            for file_path in file_paths:
                with Image.open(file_path) as image:
                    if not self.frames:
                        self.base_size = image.size
                    image = self.resize_to_base_size(image.copy())
                    self.frames.append(image)
                self.delays.append(100)
                var = IntVar()
                var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
                self.checkbox_vars.append(var)

            self.update_frame_list()
            self.show_frame()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add images: {e}")

    def add_empty_frame(self):
        """Add an empty frame with optional background color."""
        if not self.frames:
            messagebox.showerror("Error", "No frames available to determine the size for the new frame.")
            return

        # Prompt the user for the background color in hexadecimal format
        color_code = simpledialog.askstring("Add Empty Frame", "Enter background color (hex code, e.g., #FFFFFF for white):")
        
        # Validate and set the color, default to transparent if invalid
        if color_code and len(color_code) == 7 and color_code[0] == '#':
            try:
                # Test the color code by creating a single pixel image
                Image.new("RGBA", (1, 1), color_code).verify()
            except ValueError:
                messagebox.showerror("Invalid Color", "The entered color code is invalid. Using transparent background instead.")
                color_code = None
        else:
            color_code = None

        self.save_state()  # Save the state before making changes

        # Create a new empty frame with the specified or default color
        try:
            new_frame = Image.new("RGBA", self.frames[0].size, color_code if color_code else (0, 0, 0, 0))
        except IndexError as e:
            messagebox.showerror("Error", f"Failed to create a new frame: {e}")
            return

        self.frames.append(new_frame)
        self.delays.append(100)  # Default delay for new frame
        var = IntVar()
        var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
        self.checkbox_vars.append(var)

        self.update_frame_list()
        self.show_frame()


    def resize_to_max_dimensions(self, image):
        """Resize the image to the maximum dimensions of the current frames."""
        if not self.frames:
            return image

        max_width = max(frame.width for frame in self.frames)
        max_height = max(frame.height for frame in self.frames)
        return image.resize((max_width, max_height), Image.Resampling.LANCZOS)

    def update_frame_list(self):
        """Update the listbox with the current frames and their delays."""
        for widget in self.frame_list.winfo_children():
            widget.destroy()

        if not self.frames:
            label = tk.Label(self.frame_list, text="No frames available")
            label.pack()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            return

        for i, (frame, delay) in enumerate(zip(self.frames, self.delays)):
            var = self.checkbox_vars[i]
            bg_color = 'gray' if i == self.frame_index else self.master.cget('bg')
            frame_widget = tk.Frame(self.frame_list, bg=bg_color)
            frame_widget.pack(fill=tk.X)
            checkbox = Checkbutton(frame_widget, variable=var, bg=bg_color, command=lambda i=i: self.toggle_frame(i))
            checkbox.pack(side=tk.LEFT)
            label_text = f"→ Frame {i + 1}: {delay} ms" if i == self.frame_index else f"Frame {i + 1}: {delay} ms"
            label = tk.Label(frame_widget, text=label_text, bg=bg_color)
            label.pack(side=tk.LEFT, fill=tk.X)

        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def set_current_frame(self, index):
        """Set the current frame to the one corresponding to the clicked checkbox."""
        self.frame_index = index
        self.show_frame(scroll=False)

    def show_frame(self, scroll=True):
        """Display the current frame."""
        if self.frames:
            frame = self.frames[self.frame_index]
            preview = self.resize_image(frame, max_width=800, max_height=600)
            photo = ImageTk.PhotoImage(preview)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.image_label.config(text='')
            self.delay_entry.delete(0, tk.END)
            self.delay_entry.insert(0, str(self.delays[self.frame_index]))
            self.dimension_label.config(text=f"Size: {frame.width}x{frame.height}")
            total_duration = sum(self.delays)
            self.total_duration_label.config(text=f"Total Duration: {total_duration} ms")
        else:
            self.image_label.config(image='', text="No frames to display")
            self.image_label.image = None
            self.delay_entry.delete(0, tk.END)
            self.dimension_label.config(text="")
            self.total_duration_label.config(text="")
        self.update_frame_list()
        if scroll:
            self.focus_current_frame()

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

        if self.frame_index >= len(self.frames):
            self.frame_index = max(0, len(self.frames) - 1)

        self.update_frame_list()
        self.show_frame()

    def move_frames_to_position(self):
        """Move selected frames below the frame with the specified name."""
        frame_name = tk.simpledialog.askstring("Move Frames", "Enter the name of the frame to move below (e.g., Frame 1):")
        if not frame_name:
            return

        try:
            frame_number = int(frame_name.split()[1])
        except (IndexError, ValueError):
            messagebox.showerror("Invalid Input", "Please enter a valid frame name (e.g., Frame 1).")
            return

        if frame_number < 1 or frame_number > len(self.frames):
            messagebox.showerror("Invalid Input", "Frame number out of range.")
            return

        target_index = frame_number - 1
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if not selected_indices:
            messagebox.showinfo("Info", "No frames selected to move.")
            return

        self.save_state()  # Save the state before making changes

        # Sort indices to preserve the order when re-inserting
        selected_indices.sort()

        # Collect the frames, delays, and checkboxes to be moved
        frames_to_move = [self.frames[i] for i in selected_indices]
        delays_to_move = [self.delays[i] for i in selected_indices]
        checkboxes_to_move = [self.checkbox_vars[i] for i in selected_indices]

        # Remove selected frames from the original positions
        for i in reversed(selected_indices):
            del self.frames[i]
            del self.delays[i]
            del self.checkbox_vars[i]

        # Insert the frames, delays, and checkboxes at the target position
        for i, (frame, delay, checkbox) in enumerate(zip(frames_to_move, delays_to_move, checkboxes_to_move)):
            insertion_index = target_index + 1 + i
            self.frames.insert(insertion_index, frame)
            self.delays.insert(insertion_index, delay)
            self.checkbox_vars.insert(insertion_index, checkbox)

        self.update_frame_list()
        self.show_frame()

    def move_frame_up(self, event=None):
        """Move the selected frames up in the list."""
        self.save_state()  # Save the state before making changes
        indices_to_move = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        for i in indices_to_move:
            if i > 0 and i - 1 not in indices_to_move:
                self.swap_frames(i, i - 1)
                if i == self.frame_index:
                    self.frame_index = i - 1
                elif i - 1 == self.frame_index:
                    self.frame_index = i

        self.show_frame()

    def move_frame_down(self, event=None):
        """Move the selected frames down in the list."""
        self.save_state()  # Save the state before making changes
        indices_to_move = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        for i in reversed(indices_to_move):
            if i < len(self.frames) - 1 and i + 1 not in indices_to_move:
                self.swap_frames(i, i + 1)
                if i == self.frame_index:
                    self.frame_index = i + 1
                elif i + 1 == self.frame_index:
                    self.frame_index = i

        self.show_frame()

    def swap_frames(self, i, j):
        """Swap frames and update indexes."""
        self.frames[i], self.frames[j] = self.frames[j], self.frames[i]
        self.delays[i], self.delays[j] = self.delays[j], self.delays[i]
        self.checkbox_vars[i].set(0)
        self.checkbox_vars[j].set(1)
        if i == self.frame_index:
            self.frame_index = j
        elif j == self.frame_index:
            self.frame_index = i

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
            self.show_frame(scroll=False)
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

    def save(self, event=None):
        """Save the current frames and delays to a GIF file."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as()

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
                ext = ext[1:].lower()
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
        self.redo_stack.clear()

    def copy_frames(self, event=None):
        """Copy the selected frames to the clipboard."""
        self.copied_frames = [(self.frames[i].copy(), self.delays[i]) for i in range(len(self.checkbox_vars)) if self.checkbox_vars[i].get() == 1]
        if not self.copied_frames:
            messagebox.showinfo("Info", "No frames selected to copy.")
        else:
            messagebox.showinfo("Info", f"Copied {len(self.copied_frames)} frame(s).")

    def paste_frames(self, event=None):
        """Paste the copied frames below the selected frames."""
        if not hasattr(self, 'copied_frames') or not self.copied_frames:
            messagebox.showerror("Error", "No frames to paste. Please copy frames first.")
            return

        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        if not selected_indices:
            messagebox.showinfo("Info", "No frames selected to paste after. Pasting at the end.")
            insert_index = len(self.frames)
        else:
            insert_index = max(selected_indices) + 1

        self.save_state()  # Save the state before making changes

        for frame, delay in self.copied_frames:
            self.frames.insert(insert_index, frame)
            self.delays.insert(insert_index, delay)
            var = IntVar()
            var.trace_add('write', lambda *args, i=insert_index: self.set_current_frame(i))
            self.checkbox_vars.insert(insert_index, var)
            insert_index += 1

        self.update_frame_list()
        self.show_frame()

    def undo(self, event=None):
        """Undo the last action."""
        if self.history:
            self.redo_stack.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
            self.restore_state(self.history.pop())
            self.check_all.set(False)

    def redo(self, event=None):
        """Redo the last undone action."""
        if self.redo_stack:
            self.history.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
            self.restore_state(self.redo_stack.pop())
            self.check_all.set(False)

    def apply_crossfade_effect(self):
        """Apply crossfade effect between checked frames."""
        checked_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        
        if len(checked_indices) < 2:
            messagebox.showinfo("Info", "Need at least two checked frames to apply crossfade effect.")
            return

        self.save_state()  # Save the state before making changes

        crossfade_frames = []
        crossfade_delays = []

        def blend_frames(frame1, frame2, alpha):
            """Blend two frames with given alpha."""
            return Image.blend(frame1, frame2, alpha)

        for idx in range(len(checked_indices) - 1):
            i = checked_indices[idx]
            j = checked_indices[idx + 1]
            
            frame1 = self.frames[i]
            frame2 = self.frames[j]
            crossfade_frames.append(frame1)
            crossfade_delays.append(self.delays[i])
            
            # Generate crossfade frames
            steps = 10  # Number of steps for the crossfade
            for step in range(1, steps):
                alpha = step / float(steps)
                blended_frame = blend_frames(frame1, frame2, alpha)
                crossfade_frames.append(blended_frame)
                crossfade_delays.append(self.delays[i] // steps)
        
        # Insert crossfade frames and delays at the correct positions
        for idx in range(len(checked_indices) - 1, -1, -1):
            i = checked_indices[idx]
            self.frames.pop(i)
            self.delays.pop(i)
            self.checkbox_vars.pop(i)

        insert_index = checked_indices[0]
        for frame, delay in zip(crossfade_frames, crossfade_delays):
            self.frames.insert(insert_index, frame)
            self.delays.insert(insert_index, delay)
            var = IntVar(value=1)
            var.trace_add('write', lambda *args, i=insert_index: self.set_current_frame(i))
            self.checkbox_vars.insert(insert_index, var)
            insert_index += 1

        self.update_frame_list()
        self.show_frame()

    def crop_frames_dialog(self):
        """Open a dialog to get the cropping dimensions and crop the frames."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Crop Frames")

        tk.Label(dialog, text="Crop Width:").pack(pady=5)
        width_entry = tk.Entry(dialog)
        width_entry.pack(pady=5)

        tk.Label(dialog, text="Crop Height:").pack(pady=5)
        height_entry = tk.Entry(dialog)
        height_entry.pack(pady=5)

        def crop():
            try:
                crop_width = int(width_entry.get())
                crop_height = int(height_entry.get())
                self.crop_frames(crop_width, crop_height)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid integers for width and height.")

        tk.Button(dialog, text="Crop", command=crop).pack(pady=10)
        dialog.grab_set()

    def crop_frames(self, crop_width, crop_height):
        """Crop all selected frames to the specified width and height."""
        self.save_state()  # Save the state before making changes
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                # Calculate the crop box
                left = (frame.width - crop_width) // 2
                top = (frame.height - crop_height) // 2
                right = left + crop_width
                bottom = top + crop_height
                # Crop the frame
                self.frames[i] = frame.crop((left, top, right, bottom))
        self.show_frame()
        self.update_frame_list()

    def desaturate_frames(self):
        """Apply desaturation effect to the selected frames."""
        self.save_state()  # Save the state before making changes
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                self.frames[i] = frame.convert("L").convert("RGBA")  # Convert to grayscale and then back to RGBA
        self.show_frame()
        self.update_frame_list()

    def invert_colors_frames_dialog(self):
            """Open a dialog to apply the negative effect to the selected frames."""
            dialog = tk.Toplevel(self.master)
            dialog.title("Invert Colors")

            tk.Label(dialog, text="Apply negative effect to selected frames?").pack(pady=10)

            def apply_invert_colors():
                self.apply_invert_colors_effect()
                dialog.destroy()

            tk.Button(dialog, text="Apply", command=apply_invert_colors).pack(pady=10)
            dialog.grab_set()

    def apply_invert_colors_effect(self):
        """Apply the negative effect (invert colors) to the selected frames."""
        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                self.frames[i] = ImageOps.invert(self.frames[i].convert("RGB")).convert("RGBA")

        self.show_frame()
        self.update_frame_list()

    def apply_tint(self):
        """Apply a tint effect to the selected frames."""
        # Prompt user for hex color code and intensity
        color_code = simpledialog.askstring("Tint Effect", "Enter tint color (hex code, e.g., #FF0000 for red):")
        if not color_code or not (color_code.startswith('#') and len(color_code) == 7):
            messagebox.showerror("Invalid Input", "Please enter a valid hex color code (e.g., #FF0000).")
            return
        
        intensity = simpledialog.askinteger("Tint Effect", "Enter intensity (0-100):", minvalue=0, maxvalue=100)
        if intensity is None or not (0 <= intensity <= 100):
            messagebox.showerror("Invalid Input", "Please enter an intensity value between 0 and 100.")
            return

        self.save_state()  # Save the state before making changes

        # Apply the tint effect to the selected frames
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                self.frames[i] = self.tint_image(self.frames[i], color_code, intensity)
        
        self.show_frame()
        self.update_frame_list()

    def tint_image(self, image, color_code, intensity):
        """Tint an image with the given color and intensity."""
        r, g, b = Image.new("RGB", (1, 1), color_code).getpixel((0, 0))
        intensity /= 100.0

        # Create a tinted image
        tinted_image = Image.new("RGBA", image.size)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.getpixel((x, y))
                tr = int(pixel[0] + (r - pixel[0]) * intensity)
                tg = int(pixel[1] + (g - pixel[1]) * intensity)
                tb = int(pixel[2] + (b - pixel[2]) * intensity)
                ta = pixel[3]
                tinted_image.putpixel((x, y), (tr, tg, tb, ta))

        return tinted_image

    def apply_sepia_effect_dialog(self):
        """Open a dialog to choose the sepia effect intensity."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Apply Sepia Effect")

        tk.Label(dialog, text="Sepia Intensity (0-100):").pack(pady=5)
        intensity_entry = tk.Entry(dialog)
        intensity_entry.pack(pady=5)
        intensity_entry.insert(0, "50")  # Default intensity value

        def apply_sepia():
            try:
                intensity = int(intensity_entry.get())
                if 0 <= intensity <= 100:
                    self.save_state()  # Save the state before making changes
                    self.apply_sepia_effect(intensity)
                    dialog.destroy()
                else:
                    messagebox.showerror("Invalid Input", "Please enter a value between 0 and 100.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid integer for intensity.")

        tk.Button(dialog, text="Apply", command=apply_sepia).pack(pady=10)
        dialog.grab_set()

    def apply_sepia_effect(self, intensity):
        """Apply sepia effect to the selected frames with the given intensity."""
        def apply_sepia(image, intensity):
            """Convert an image to sepia with a given intensity."""
            width, height = image.size
            pixels = image.load()  # Create a pixel map

            for py in range(height):
                for px in range(width):
                    r, g, b, a = image.getpixel((px, py))

                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)

                    tr = min(int(tr * (intensity / 100)), 255)
                    tg = min(int(tg * (intensity / 100)), 255)
                    tb = min(int(tb * (intensity / 100)), 255)

                    pixels[px, py] = (tr, tg, tb, a)

            return image

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                self.frames[i] = apply_sepia(self.frames[i], intensity)

        self.show_frame()
        self.update_frame_list()

    def reverse_frames(self):
        """Apply reverse effect to the selected frames."""
        self.save_state()  # Save the state before making changes
        indices_to_reverse = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        
        if not indices_to_reverse:
            messagebox.showinfo("Info", "No frames selected for reversing.")
            return

        # Extract the selected frames and their delays
        frames_to_reverse = [self.frames[i] for i in indices_to_reverse]
        delays_to_reverse = [self.delays[i] for i in indices_to_reverse]

        # Reverse the selected frames and their delays
        frames_to_reverse.reverse()
        delays_to_reverse.reverse()

        # Replace the selected frames and their delays with the reversed versions
        for idx, i in enumerate(indices_to_reverse):
            self.frames[i] = frames_to_reverse[idx]
            self.delays[i] = delays_to_reverse[idx]

        self.show_frame()
        self.update_frame_list()

    def rotate_frames_dialog(self):
        """Open a dialog to choose and apply rotation effects to selected frames."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Rotate Frames")

        tk.Label(dialog, text="Select rotation effect:").pack(pady=5)

        options = ["Flip Vertical", "Flip Horizontal", "Rotate 90° Clockwise", "Rotate 90° Counter-Clockwise", "Rotate 180°", "Rotate Custom"]
        rotation_var = tk.StringVar(value=options[0])
        dropdown = tk.OptionMenu(dialog, rotation_var, *options)
        dropdown.pack(pady=5)

        custom_angle_label = tk.Label(dialog, text="Enter angle (degrees):")
        custom_angle_label.pack(pady=5)
        custom_angle_label.pack_forget()  # Hide initially
        custom_angle_entry = tk.Entry(dialog)
        custom_angle_entry.pack(pady=5)
        custom_angle_entry.pack_forget()  # Hide initially

        def on_option_change(*args):
            if rotation_var.get() == "Rotate Custom":
                custom_angle_label.pack(pady=5)
                custom_angle_entry.pack(pady=5)
            else:
                custom_angle_label.pack_forget()
                custom_angle_entry.pack_forget()

        rotation_var.trace_add('write', on_option_change)

        def apply_rotation():
            option = rotation_var.get()
            angle = 0
            if option == "Rotate Custom":
                try:
                    angle = int(custom_angle_entry.get())
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter a valid integer for the custom angle.")
                    return

            self.apply_rotation_effect(option, angle)
            dialog.destroy()

        tk.Button(dialog, text="Apply", command=apply_rotation).pack(pady=10)
        dialog.grab_set()

    def apply_rotation_effect(self, option, custom_angle):
        """Apply the selected rotation effect to the checked frames."""
        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                if option == "Flip Vertical":
                    self.frames[i] = ImageOps.flip(self.frames[i])
                elif option == "Flip Horizontal":
                    self.frames[i] = ImageOps.mirror(self.frames[i])
                elif option == "Rotate 90° Clockwise":
                    self.frames[i] = self.frames[i].rotate(-90, expand=True)
                elif option == "Rotate 90° Counter-Clockwise":
                    self.frames[i] = self.frames[i].rotate(90, expand=True)
                elif option == "Rotate 180°":
                    self.frames[i] = self.frames[i].rotate(180, expand=True)
                elif option == "Rotate Custom":
                    self.frames[i] = self.frames[i].rotate(custom_angle, expand=True)

        self.show_frame()
        self.update_frame_list()

    def restore_state(self, state):
        """Restore the state of the editor."""
        self.frames, self.delays, checkbox_states, self.frame_index, self.current_file = state
        self.checkbox_vars = [IntVar(value=state) for state in checkbox_states]
        for i, var in enumerate(self.checkbox_vars):
            var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
        self.base_size = self.frames[0].size if self.frames else None
        self.update_frame_list()
        self.show_frame()
        self.update_title()

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

    def toggle_frame(self, index):
        """Toggle the checkbox of the frame without scrolling."""
        self.checkbox_vars[index].set(0 if self.checkbox_vars[index].get() else 1)
        self.update_frame_list()

    def toggle_checkbox(self, event=None):
        """Toggle the checkbox of the current frame without scrolling."""
        if self.checkbox_vars:
            current_var = self.checkbox_vars[self.frame_index]
            current_var.set(0 if current_var.get() else 1)
            self.update_frame_list()

    def show_about(self):
        """Display the About dialog."""
        messagebox.showinfo("About GIFCraft", "GIFCraft - GIF Editor\nVersion 1.0\n© 2024 by Seehrum")

    def reset_editor_state(self):
        """Reset the editor to its initial state."""
        self.frames = []
        self.delays = []
        self.checkbox_vars = []
        self.current_file = None
        self.frame_index = 0
        self.base_size = None
        self.update_frame_list()
        self.show_frame()
        self.update_title()

    def reset_frames_and_vars(self):
        """Reset frames and associated variables."""
        self.frames = []
        self.delays = []
        self.checkbox_vars = []
        for widget in self.frame_list.winfo_children():
            widget.destroy()

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
