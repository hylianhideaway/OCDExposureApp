import tkinter as tk
from tkinter import filedialog, messagebox
import time
import csv
import matplotlib.pyplot as plt

class OCDExposureApp(tk.Tk):
    """
    A simplified Tkinter application for OCD exposure tracking.
    - Press 'Start' to begin the timer.
    - Press 'Stop' to end the timer and immediately see the results (data + plot).
    """
    def __init__(self):
        super().__init__()
        self.title("OCD Exposure Tracking Tool")

        # Timer variables
        self.start_time = None
        self.running = False
        self.elapsed_time = 0
        #Stores user data
        self.data = []

        # Build the user interface
        self.create_widgets()

        # Update the timer display periodically
        self.update_timer()

    def create_widgets(self):
        # Stopwatch label (shows elapsed time)
        self.timer_label = tk.Label(self, text="0", font=("Helvetica", 24))
        self.timer_label.grid(row=0, column=0, columnspan=4, pady=10)

        # Display area for recent (time, rating) pairs
        self.data_frame = tk.Frame(self)
        self.data_frame.grid(row=1, column=0, columnspan=4, pady=10)
        self.data_text = tk.Text(self.data_frame, width=40, height=5, state='disabled', font=("Helvetica", 12))
        self.data_text.pack()

        # Buttons for ratings 1–10
        self.buttons = {}
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        positions = {
            1: (2, 0), 2: (2, 1), 3: (2, 2),
            4: (3, 0), 5: (3, 1), 6: (3, 2),
            7: (4, 0), 8: (4, 1), 9: (4, 2),
            10: (5, 0)
        }
        for num in numbers:
            btn = tk.Button(self, text=str(num), font=("Helvetica", 18), width=5, height=2,
                            command=lambda n=num: self.record_rating(n))
            row, col = positions[num]
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.buttons[num] = btn

        # Start/Stop button
        self.start_stop_button = tk.Button(self, text="Start", font=("Helvetica", 18), width=10, height=2,
                                           command=self.toggle_timer)
        self.start_stop_button.grid(row=5, column=1, padx=5, pady=5)

    def update_timer(self):
        """
        Periodically update the displayed time if the timer is running.
        """
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            # Show whole seconds only
            self.timer_label.config(text=f"{self.get_DisplayTime_String(self.elapsed_time)}")
        self.after(100, self.update_timer)

    def toggle_timer(self):
        """
        Start the timer if it's not running, or stop the timer if it is.
        Once stopped, immediately show the results.
        """
        if not self.running:
            self.start_timer()
            self.start_stop_button.config(text="Stop")
        else:
            self.stop_timer()
            self.start_stop_button.config(text="Start")
            self.show_results()

    def start_timer(self):
        """
        Begin (or resume) timing.
        """
        if not self.running:
            self.running = True
            # Adjust start_time for already elapsed_time (if any), so it can resume.
            self.start_time = time.time() - self.elapsed_time

    def stop_timer(self):
        """
        Stop the timer.
        """
        self.running = False

    def record_rating(self, rating):
        """
        Record a rating if the timer is running, along with the current elapsed time.
        """
        if self.running:
            current_time = time.time() - self.start_time
            self.data.append((current_time, rating))
            self.update_data_display(current_time, rating)

    
    def update_data_display(self,current_time, rating):
        """
        Adds a new data entry pair to the widget
        and automatically scroll so the new text is visible.
        """
        self.data_text.config(state='normal')
        #self.data_text.delete(1.0, tk.END)
        
        self.data_text.insert(tk.END,  self.get_DisplayTime_String(current_time)+f"   {rating}\n")
        
        # Scroll to the bottom (end) of the text widget
        self.data_text.see(tk.END)
        
        self.data_text.config(state='disabled')

    def show_results(self):
        """
        Open a new window showing the full dataset and a simple plot of time vs. rating.
        Also provide a button to save the data as CSV.
        """
        # Disable rating buttons once results are shown
        for btn in self.buttons.values():
            btn.config(state='disabled')
        self.start_stop_button.config(state='disabled')

        results_window = tk.Toplevel(self)
        results_window.title("Session Results")

        # Display the full dataset in a text widget
        dataset_text = tk.Text(results_window, width=50, height=15, font=("Helvetica", 12))
        dataset_text.pack(pady=10)
        dataset_text.insert(tk.END, "Time (s), Rating\n")
        for t, rating in self.data:
            dataset_text.insert(tk.END, f"{t:.2f}, {rating}\n")
        dataset_text.config(state='disabled')

        # If data is present, plot it
        if self.data:
            times, ratings = zip(*self.data)
            fig, ax = plt.subplots()
            ax.plot(times, ratings, marker='o')
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Rating")
            ax.set_ylim(0, 11)  # y-axis from 0 to 10
            ax.set_title("Rating over Time")
            plt.show()

        # Button to save results
        save_button = tk.Button(results_window, text="Save Results", font=("Helvetica", 14),
                                command=self.save_results)
        save_button.pack(pady=10)

    def save_results(self):
        """
        Prompt the user for a filename and save the data to a CSV file.
        """
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV Files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Time (s)", "Rating"])
                for t, rating in self.data:
                    writer.writerow([f"{t:.2f}", rating])
            messagebox.showinfo("Save", "Results saved successfully!")


    def  get_DisplayTime_String(self,seconds:float):
        min = seconds//60
        remainingSeconds = seconds%60
        return f"{min:.0f}:{remainingSeconds:.0f}"



if __name__ == "__main__":
    app = OCDExposureApp()
    app.mainloop()
