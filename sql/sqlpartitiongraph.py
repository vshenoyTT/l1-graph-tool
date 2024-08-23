import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def plot_buffers(sqlite_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(sqlite_file)
    
    query = "SELECT operation_id, address, max_size_per_bank FROM buffers"
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(df)
    # Pivot the DataFrame for stacked bar plotting
    pivot_df = df.pivot_table(index='operation_id', columns='address', values='max_size_per_bank', fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot the stacked bar graph
    pivot_df.plot(kind='bar', stacked=True, ax=ax, alpha=0.7, legend=False)

    ax.set_xlabel('Operation ID')
    ax.set_ylabel('L1 Buffer Size')
    ax.set_title('L1 Utilization Visualizer')
    ax.grid(True, axis='y')
    ax.set_xticks([])
    
    plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot buffers from SQLite file.')
    parser.add_argument('sqlite_file', type=str, help='Path to the SQLite file')
    args = parser.parse_args()
    
    plot_buffers(args.sqlite_file)
