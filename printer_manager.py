import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

np.seterr(divide='ignore', invalid='ignore')

# Global variables to simulate printer statistics
total_pages_printed = 0
total_print_jobs = 0
total_print_time = 0
total_ink_usage = 0

# Simulated job data (to be updated dynamically)
jobs = []

# Dictionary to track printer status
printer_status = {}

def get_printers():
    return ["Printer 1", "Printer 2", "Printer 3"]

def get_printer_status(printer_id):
    if printer_id in printer_status:
        return printer_status[printer_id]
    else:
        return "Ready"

def send_print_job(printer_id, pages, options):
    global jobs, printer_status

    # Update printer status to "Busy"
    printer_status[printer_id] = "Busy"

    # Simulate print time (30 seconds per job)
    print_time = 30.0

    # Simulate ink usage (2% per page)
    ink_usage = pages * 2

    # Generate job ID
    job_id = f"Job{len(jobs) + 1}"

    # Add job to the jobs list
    jobs.append({
        "job_id": job_id,
        "printer_id": printer_id,
        "pages": pages,
        "print_time": print_time,
        "ink_usage": ink_usage,
        "start_time": None,
        "end_time": None,
        "status": "printing"
    })

    # Simulate printing in a separate thread
    threading.Thread(target=complete_print_job, args=(job_id, print_time)).start()

def complete_print_job(job_id, print_time):
    global jobs, printer_status
    time.sleep(print_time)  # Simulate printing time
    for job in jobs:
        if job["job_id"] == job_id and job["status"] == "printing":
            job["status"] = "completed"
            job["end_time"] = time.time()
            # Update printer status to "Ready" when job completes
            printer_status[job["printer_id"]] = "Ready"

def cancel_print_job(printer_id, job_id):
    global jobs, printer_status
    for job in jobs:
        if job["job_id"] == job_id and job["status"] == "printing":
            job["status"] = "cancelled"
            # Update printer status to "Ready" when job is cancelled
            printer_status[printer_id] = "Ready"
            return True
    return False

def get_print_queue(printer_id):
    global jobs
    return [job["job_id"] for job in jobs if job["status"] != "printing" and job["printer_id"] == printer_id]

def perform_maintenance(printer_id, task):
    global jobs, printer_status

    # Assuming task is to empty all queues
    if task == "Empty Queue":
        for job in jobs:
            if job["printer_id"] == printer_id and job["status"] == "printing":
                job["status"] = "cancelled"
        # Update printer status to "Ready"
        printer_status[printer_id] = "Ready"
        return True
    else:
        # Handle other maintenance tasks here if needed
        return False

def get_printer_statistics(printer_id):
    global jobs

    completed_jobs = [job for job in jobs if job["status"] == "completed"]

    total_pages_printed = sum(job["pages"] for job in completed_jobs)
    total_print_jobs = len(completed_jobs)
    total_print_time = sum(job["print_time"] for job in completed_jobs)
    total_ink_usage = sum(job["ink_usage"] for job in completed_jobs)

    avg_print_time = total_print_time / total_print_jobs if total_print_jobs > 0 else 0

    # Alert if ink usage is greater than 80%
    if total_ink_usage > 80:
        messagebox.showwarning("Warning", "Ink usage is greater than 80%")
        printer_status[printer_id] = "Low Ink"

    return {
        "total_pages": total_pages_printed,
        "total_jobs": total_print_jobs,
        "total_time": total_print_time,
        "avg_print_time": avg_print_time,
        "ink_usage": total_ink_usage
    }

def reset_printer_statistics(printer_id):
    global jobs, printer_status

    # Example: Clear completed jobs for the printer
    global jobs
    jobs = [job for job in jobs if job["printer_id"] != printer_id or job["status"] != "completed"]

    # Reset other statistics if needed
    return True  # Return True if reset successful, otherwise False

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

        # Initialize printer status (default to "Ready")
        printers = get_printers()
        for printer in printers:
            printer_status[printer] = "Ready"

        # Bind the closing event
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Set up periodic updates
        self.after_id = self.master.after(5000, self.periodic_update)

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
        ttk.Button(self.main_frame, text="Send Print Job", command=self.send_print_job_handler).pack(pady=5)
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
        maintenance_tasks = ["Clean Print Heads", "Align Cartridges", "Update Firmware", "Empty Queue"]
        self.maintenance_var = tk.StringVar()
        ttk.Combobox(self.main_frame, textvariable=self.maintenance_var, values=maintenance_tasks).pack(pady=5)
        ttk.Button(self.main_frame, text="Perform Maintenance", command=self.perform_maintenance).pack(pady=5)

    def setup_stats_frame(self):
        # Statistics display
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 10))
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

    def send_print_job_handler(self):
        printer_id = self.printer_var.get()
        if printer_id:
            # Simulated job with 2 pages
            pages = 2
            options = {
                "duplex": self.duplex_var.get(),
                "color": self.color_var.get()
            }
            try:
                send_print_job(printer_id, pages, options)
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

        if stats:
            labels = ["Total Pages Printed", "Average Print Time"]
            values = [stats["total_pages"], stats["avg_print_time"]]
            
            # Ensure we're not dividing by zero
            if sum(values) > 0:
                colors = ['gold', 'yellowgreen']
                explode = (0.1, 0)

                self.ax1.pie(values, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
                self.ax1.axis('equal')

                self.ax2.bar(labels, values, color=colors)
                self.ax2.set_ylabel('Count')
            else:
                self.ax1.text(0.5, 0.5, "No data to display", ha='center', va='center')
                self.ax2.text(0.5, 0.5, "No data to display", ha='center', va='center')

        self.fig.tight_layout()
        self.canvas.draw()

    def reset_statistics(self):
        printer_id = self.printer_var.get()
        if printer_id:
            try:
                success = reset_printer_statistics(printer_id)
                if success:
                    messagebox.showinfo("Reset Statistics", "Statistics reset successfully")
                    self.plot_statistics({})
                else:
                    messagebox.showerror("Reset Statistics", "Failed to reset statistics")
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
                    messagebox.showerror("Error", f"Failed to perform maintenance task '{task}'")
            except Exception as e:
                self.show_error("Error performing maintenance", e)

    def periodic_update(self):
        self.update_status()
        self.update_queue()
        self.update_statistics()
        self.after_id = self.master.after(5000, self.periodic_update)

    def on_closing(self):
        if hasattr(self, 'after_id'):
            self.master.after_cancel(self.after_id)
        self.master.destroy()

    def show_error(self, message, exception):
        messagebox.showerror("Error", f"{message}: {exception}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PrinterManager(root)
    root.mainloop()
