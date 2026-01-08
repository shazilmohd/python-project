import tkinter as tk
from tkinter import ttk


class ColorPoll:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Poll")
        self.root.geometry("400x300")
        
        # Dictionary mapping color codes to actual colors and display names
        self.colors = {
            'R': {'name': 'Red', 'code': '#FF0000'},
            'G': {'name': 'Green', 'code': '#00AA00'},
            'Y': {'name': 'Yellow', 'code': '#FFFF00'},
            'B': {'name': 'Blue', 'code': '#0000FF'}
        }
        
        # Variable to track selected color
        self.selected_color = tk.StringVar(value='')
        
        # Create title label
        title_label = tk.Label(
            self.root,
            text="Select Your Favorite Color",
            font=("Arial", 14, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Create frame for poll options
        poll_frame = tk.Frame(self.root)
        poll_frame.pack(pady=20)
        
        # Create radio buttons for each color
        for color_code in ['R', 'G', 'Y', 'B']:
            color_info = self.colors[color_code]
            radio_btn = tk.Radiobutton(
                poll_frame,
                text=f"{color_code} - {color_info['name']}",
                variable=self.selected_color,
                value=color_code,
                font=("Arial", 12),
                command=self.on_color_selected,
                pady=10
            )
            radio_btn.pack(anchor=tk.W, padx=20)
        
        # Create a label to display current selection
        self.status_label = tk.Label(
            self.root,
            text="No color selected",
            font=("Arial", 11),
            pady=10,
            fg="gray"
        )
        self.status_label.pack()
        
        # Initialize window background
        self.root.config(bg='white')
    
    def on_color_selected(self):
        """Handle color selection"""
        selected = self.selected_color.get()
        
        if selected:
            color_info = self.colors[selected]
            color_code = color_info['code']
            color_name = color_info['name']
            
            # Change window background to selected color
            self.root.config(bg=color_code)
            
            # Update status label
            self.status_label.config(
                text=f"Selected: {color_name}",
                fg="white" if selected in ['R', 'B'] else "black"
            )


def main():
    root = tk.Tk()
    app = ColorPoll(root)
    root.mainloop()


if __name__ == "__main__":
    main()
