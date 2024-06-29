import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random  # For simulating some API calls
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Simulated API functions
def get_printers():
    return ["Printer 1", "Printer 2", "Printer 3"]

def get_printer_status(printer_id):
    statuses = ["Ready", "Busy", "Error", "Low Ink"]
    return random.choice(statuses)

def send_print_job(printer_id, document, options):
    return f"Job{random.randint(1000, 9999)}"

def cancel_print_job(printer_id, job_id):
    return True

def get_print_queue(printer_id):
    return [f"Job{random.randint(1000, 9999)}" for _ in range(random.randint(0, 5))]

def perform_maintenance(printer_id, task):
    return True

def get_printer_statistics(printer_id):
    return {
        "total_pages": random.randint(100, 1000),
        "avg_print_time": random.randint(10, 60),
        "ink_usage": random.randint(10, 90)
    }

def reset_printer_statistics(printer_id):
    return True

class PrinterManager:
    def __init__(self, master):
        self.master = master
        master.title("Printer Manager")
        master.geometry("700x800")

        # Create tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        self.main_frame = ttk.Frame(self.notebook)
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Printer Control")
        self.notebook.add(self.stats_frame, text="Statistics")

        self.setup_main_frame()
        self.setup_stats_frame()

        # Set up periodic updates
        self.master.after(5000, self.periodic_update)

    def setup_main_frame(self):
        # Printer selection
        ttk.Label(self.main_frame, text="Select Printer:").pack(pady=5)
        self.printer_var = tk.StringVar()
        self.printer_combo = ttk.Combobox(self.main_frame, textvariable=self.printer_var)
        self.printer_combo.pack()
        self.update_printer_list()

        # Printer status
        self.status_label = ttk.Label(self.main_frame, text="Status: N/A")
        self.status_label.pack(pady=5)

        # Print settings
        ttk.Label(self.main_frame, text="Print Settings:").pack(pady=5)
        self.duplex_var = tk.BooleanVar()
        ttk.Checkbutton(self.main_frame, text="Duplex Mode", variable=self.duplex_var).pack()
        self.color_var = tk.BooleanVar()
        ttk.Checkbutton(self.main_frame, text="Color Mode", variable=self.color_var).pack()

        # Print job options
        ttk.Button(self.main_frame, text="Send Print Job", command=self.send_print_job).pack(pady=5)
        ttk.Button(self.main_frame, text="Cancel Print Job", command=self.cancel_print_job).pack(pady=5)

        # Print queue
        self.queue_frame = ttk.LabelFrame(self.main_frame, text="Print Queue")
        self.queue_frame.pack(pady=10, padx=10, fill="x")
        self.queue_listbox = tk.Listbox(self.queue_frame, height=5)
        self.queue_listbox.pack(fill="x")

        # Update buttons
        ttk.Button(self.main_frame, text="Update Status", command=self.update_status).pack(pady=5)
        ttk.Button(self.main_frame, text="Update Queue", command=self.update_queue).pack(pady=5)

        # Maintenance options
        maintenance_tasks = ["Clean Print Heads", "Align Cartridges", "Update Firmware"]
        self.maintenance_var = tk.StringVar()
        ttk.Combobox(self.main_frame, textvariable=self.maintenance_var, values=maintenance_tasks).pack(pady=5)
        ttk.Button(self.main_frame, text="Perform Maintenance", command=self.perform_maintenance).pack(pady=5)

    def setup_stats_frame(self):
        # Statistics display
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.stats_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ttk.Button(self.stats_frame, text="Update Statistics", command=self.update_statistics).pack(pady=5)
        ttk.Button(self.stats_frame, text="Reset Statistics", command=self.reset_statistics).pack(pady=5)

    def update_printer_list(self):
        try:
            printers = get_printers()
            self.printer_combo['values'] = printers
            if printers:
                self.printer_combo.set(printers[0])
        except Exception as e:
            self.show_error("Failed to get printer list", e)

    def update_status(self):
        printer_id = self.printer_var.get()
        if printer_id:
            try:
                status = get_printer_status(printer_id)
                self.status_label.config(text=f"Status: {status}")
            except Exception as e:
                self.show_error("Failed to get printer status", e)

    def send_print_job(self):
        printer_id = self.printer_var.get()
        if printer_id:
            file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
            if file_path:
                options = {
                    "duplex": self.duplex_var.get(),
                    "color": self.color_var.get()
                }
                try:
                    job_id = send_print_job(printer_id, file_path, options)
                    messagebox.showinfo("Print Job", f"Job sent: {job_id}")
                    self.update_queue()
                except Exception as e:
                    self.show_error("Failed to send print job", e)

    def cancel_print_job(self):
        printer_id = self.printer_var.get()
        selected = self.queue_listbox.curselection()
        if printer_id and selected:
            job_id = self.queue_listbox.get(selected[0])
            try:
                if cancel_print_job(printer_id, job_id):
                    messagebox.showinfo("Cancel Job", f"Job {job_id} cancelled")
                    self.update_queue()
                else:
                    messagebox.showerror("Error", "Failed to cancel job")
            except Exception as e:
                self.show_error("Error cancelling job", e)

    def update_queue(self):
        printer_id = self.printer_var.get()
        if printer_id:
            try:
                queue = get_print_queue(printer_id)
                self.queue_listbox.delete(0, tk.END)
                for job in queue:
                    self.queue_listbox.insert(tk.END, job)
            except Exception as e:
                self.show_error("Failed to update queue", e)

    def update_statistics(self):
        printer_id = self.printer_var.get()
        if printer_id:
            try:
                stats = get_printer_statistics(printer_id)
                self.plot_statistics(stats)
            except Exception as e:
                self.show_error("Failed to update statistics", e)

    def plot_statistics(self, stats):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.bar(['Total Pages'], [stats['total_pages']])
        self.ax1.set_title('Total Pages Printed')

        self.ax2.bar(['Avg Print Time'], [stats['avg_print_time']])
        self.ax2.set_title('Average Print Time (s)')

        self.ax3.bar(['Ink Usage'], [stats['ink_usage']])
        self.ax3.set_title('Ink Usage (%)')

        self.fig.tight_layout()
        self.canvas.draw()

    def reset_statistics(self):
        printer_id = self.printer_var.get()
        if printer_id:
            try:
                if reset_printer_statistics(printer_id):
                    messagebox.showinfo("Statistics", "Statistics reset successfully")
                    self.update_statistics()
                else:
                    messagebox.showerror("Error", "Failed to reset statistics")
            except Exception as e:
                self.show_error("Error resetting statistics", e)

    def perform_maintenance(self):
        printer_id = self.printer_var.get()
        task = self.maintenance_var.get()
        if printer_id and task:
            try:
                if perform_maintenance(printer_id, task):
                    messagebox.showinfo("Maintenance", f"{task} completed successfully")
                else:
                    messagebox.showerror("Error", f"Failed to perform {task}")
            except Exception as e:
                self.show_error("Error during maintenance", e)

    def periodic_update(self):
        self.update_status()
        self.update_queue()
        self.update_statistics()
        self.master.after(5000, self.periodic_update)  # Schedule next update in 5 seconds

    def show_error(self, message, exception):
        full_message = f"{message}: {str(exception)}"
        messagebox.showerror("Error", full_message)
        print(f"Error: {full_message}")  # Log to console as well

if __name__ == "__main__":
    root = tk.Tk()
    app = PrinterManager(root)
    root.mainloop()