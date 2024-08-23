import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import mplcursors

def plot_buffers(sqlite_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(sqlite_file)
    
    # Modified query to join with the operations table to get the operation name
    query = """
    SELECT buffers.operation_id, operations.name as operation_name, buffers.address, buffers.max_size_per_bank
    FROM buffers
    JOIN operations ON buffers.operation_id = operations.operation_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Pivot the DataFrame for stacked bar plotting
    pivot_df = df.pivot_table(index=['operation_id', 'operation_name'], columns='max_size_per_bank', values='max_size_per_bank', fill_value=0)

    pivot_df.index = pivot_df.index.set_levels(
        [pivot_df.index.levels[0], pivot_df.index.levels[1].str[5:]],
        level=['operation_id', 'operation_name']
    )

    # Create the main window
    root = tk.Tk()
    root.title("L1 Utilization Visualizer")

    # Set the window size (increase the size as needed)
    root.geometry("1600x1000")  # Increase the window size for better display

    # Create a notebook (tab control)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill='both')

    # Split the DataFrame into chunks of 50 operations each
    chunk_size = 50
    num_chunks = len(pivot_df) // chunk_size + (1 if len(pivot_df) % chunk_size != 0 else 0)
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk_df = pivot_df.iloc[start_idx:end_idx]

        # Create a new tab
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=f'Ops {start_idx}-{end_idx-1}')

        # Create a figure and plot the chunk
        fig, ax = plt.subplots(figsize=(12, 10), dpi=60)  # Adjust the figure size and DPI
        bars = chunk_df.plot(kind='bar', stacked=True, ax=ax, alpha=0.7, legend=False)

        ax.set_xlabel('Operation ID')
        ax.set_ylabel('L1 Buffer Size')
        ax.set_title(f'L1 Utilization Visualizer (Ops {start_idx}-{end_idx-1})')
        ax.grid(True, axis='y')

        # Remove x-ticks and x-tick labels
        ax.set_xticks([])  # Remove the x-ticks
        ax.set_xticklabels([])  # Remove x-tick labels

        # Adjust layout to prevent clipping
        fig.tight_layout()

        # Define a callback function for the cursor
        def make_cursor_callback(local_chunk_df):
            def on_add(sel):
                idx = sel.target.index
                operation_name = local_chunk_df.index[idx][1]
                sel.annotation.set_text(operation_name)
            return on_add

        # Add tooltips to display operation names on hover
        cursor = mplcursors.cursor(bars, hover=True)
        cursor.connect("add", make_cursor_callback(chunk_df))

        # Create a canvas and add the figure to it
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    root.mainloop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot buffers from SQLite file.')
    parser.add_argument('sqlite_file', type=str, help='Path to the SQLite file')
    args = parser.parse_args()
    
    plot_buffers(args.sqlite_file)
