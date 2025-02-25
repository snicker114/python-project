import socket
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class FileClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

    def request_directories(self):
        directories = self.client_socket.recv(1024 * 1024).decode('utf-8')
        return directories

    def navigate_folder(self, folder_path):
        self.client_socket.send(folder_path.encode('utf-8'))
        response = self.client_socket.recv(1024 * 1024).decode('utf-8')
        return response

    def download_file(self, file_path, download_path):
        try:
            self.client_socket.send(f"get {file_path}".encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')

            if response == "Sending file...":
                with open(download_path, 'wb') as file:
                    while True:
                        file_data = self.client_socket.recv(4096)  # Increased buffer size
                        if not file_data:
                            break
                        if b"DONE" in file_data:
                            file.write(file_data.replace(b"DONE", b""))  # Write the file excluding 'DONE'
                            break
                        file.write(file_data)
                return f"File downloaded successfully at {download_path}."
            else:
                return response
        except Exception as e:
            print(f"Error during file download: {str(e)}")
            return f"Error during file download: {str(e)}"


class FileClientGUI:
    def __init__(self, root):
        self.client = FileClient()
        self.root = root
        self.root.title("File Client")
        self.root.geometry("960x540")

        # Default theme is Light Mode
        self.theme = "light"

        # Configure Treeview style
        self.style = ttk.Style()

        # Control frame
        self.frame_controls = tk.Frame(root)
        self.frame_controls.pack(side=tk.TOP, fill=tk.X)

        self.connect_button = tk.Button(self.frame_controls, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.disconnect_button = tk.Button(self.frame_controls, text="Disconnect", command=self.disconnect_from_server, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.back_button = tk.Button(self.frame_controls, text="Back", command=self.go_back, state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Add Theme Switcher
        self.theme_button = tk.Button(self.frame_controls, text="Dark Mode", command=self.toggle_theme)
        self.theme_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Add Search Bar
        self.search_entry = tk.Entry(self.frame_controls, width=30)
        self.search_entry.pack(side=tk.RIGHT, padx=5, pady=5)

        self.search_button = tk.Button(self.frame_controls, text="Search", command=self.search_files)
        self.search_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Initialize Listbox (Replaces Treeview)
        self.listbox_frame = tk.Frame(root)  # Create a frame to hold the Listbox and Scrollbar
        self.listbox_frame.pack(fill=tk.BOTH, expand=True)

        # Listbox
        self.listbox = tk.Listbox(self.listbox_frame, bg="white", fg="black", selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for Listbox
        self.listbox_scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview)
        self.listbox_scrollbar.pack(side=tk.RIGHT, fill="y")

        # Attach the scrollbar to the listbox
        self.listbox.config(yscrollcommand=self.listbox_scrollbar.set)

        self.current_folder = "C:\\"
        self.folder_stack = []
        self.dark_mode = False

        # Store all buttons and entries for dynamic theme changes
        self.buttons = [
            self.connect_button,
            self.disconnect_button,
            self.back_button,
            self.search_button,
            self.theme_button,
        ]
        self.entries = [self.search_entry]

        # Apply the initial theme configuration
        self.configure_theme()

        # Bind double-click event to listbox
        self.listbox.bind("<Double-1>", self.on_item_double_click)

    def configure_theme(self):
        """Configures widget styles for light or dark mode."""
        if self.theme == "light":
            # Light Mode Styles
            self.root.configure(bg="lightgray")
            self.frame_controls.configure(bg="lightgreen")

            for button in self.buttons:
                button.configure(bg="lightgray", fg="black", activebackground="white", activeforeground="black")
            for entry in self.entries:
                entry.configure(bg="white", fg="black", insertbackground="black")

            self.listbox.config(bg="white", fg="black", selectbackground="blue", selectforeground="white")
            self.listbox_scrollbar.config(bg="lightgray")  # Reset scrollbar bg color

        else:
            # Dark Mode Styles
            self.root.configure(bg="black")
            self.frame_controls.configure(bg="black")

            for button in self.buttons:
                button.configure(bg="gray4", fg="white", activebackground="darkorange", activeforeground="white")
            for entry in self.entries:
                entry.configure(bg="gray4", fg="white", insertbackground="white")

            self.listbox.config(bg="gray4", fg="white", selectbackground="darkorange", selectforeground="white")
            self.listbox_scrollbar.config(bg="gray4")  # Apply dark mode to scrollbar

    def toggle_theme(self):
        """Switch between light and dark mode."""
        self.theme = "dark" if self.theme == "light" else "light"
        self.configure_theme()
        self.theme_button.config(text="Light Mode" if self.theme == "dark" else "Dark Mode")

    def connect_to_server(self):
        try:
            self.client.connect()
            self.update_listbox(self.client.request_directories().split('\n'))
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.back_button.config(state=tk.NORMAL)
            self.folder_stack = [self.current_folder]
            messagebox.showinfo("Connection", "Connected to server successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")

    def disconnect_from_server(self):
        self.client.disconnect()
        self.listbox.delete(0, tk.END)
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.DISABLED)
        messagebox.showinfo("Disconnection", "Disconnected from server.")

    def update_listbox(self, items):
        self.listbox.delete(0, tk.END)  # Clear the listbox first
        for item in items:
            self.listbox.insert(tk.END, item)

    def on_item_double_click(self, event):
        """Handle double-click event to either enter a folder or download a file"""
        selected_item_index = self.listbox.curselection()
        if selected_item_index:
            item_name = self.listbox.get(selected_item_index)
            full_path = os.path.join(self.current_folder, item_name)

            try:
                # Request navigation to the folder/file
                response = self.client.navigate_folder(full_path)

                if "does not exist" in response or "empty" in response:
                    # Check if it's a file instead
                    download_path = filedialog.asksaveasfilename(title="Save File As", initialfile=item_name)
                    if download_path:  # Ensure the user selected a file path
                        message = self.client.download_file(full_path, download_path)
                        messagebox.showinfo("Download", message)
                else:
                    # It's a folder, update the view
                    self.current_folder = full_path
                    self.folder_stack.append(self.current_folder)
                    self.update_listbox(response.split('\n'))

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def go_back(self):
        if len(self.folder_stack) > 1:
            self.folder_stack.pop()
            self.current_folder = self.folder_stack[-1]
            try:
                response = self.client.navigate_folder(self.current_folder)
                self.update_listbox(response.split('\n'))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Navigation", "Already at the root folder.")

    def search_files(self):
        query = self.search_entry.get().strip()
        if not query:
            # If no query is entered, show the current directory
            try:
                response = self.client.navigate_folder(self.current_folder)
                self.update_listbox(response.split('\n'))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch current directory: {str(e)}")
            return

        try:
            # Send search query to the server
            self.client.client_socket.send(f"search {query}".encode('utf-8'))
            response = self.client.client_socket.recv(1024 * 1024).decode('utf-8')

            if "No matches found" in response:
                messagebox.showinfo("Search", "No files or folders matched your search.")
            else:
                # Update the listbox with the search results
                self.update_listbox(response.split('\n'))

        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileClientGUI(root)
    root.mainloop()
