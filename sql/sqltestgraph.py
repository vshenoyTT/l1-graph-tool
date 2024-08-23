import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_buffers(sqlite_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(sqlite_file)
    
    query = "SELECT operation_id, address, max_size_per_bank FROM buffers"
    df = pd.read_sql_query(query, conn)
    print(df)
    conn.close()

    fig, ax = plt.subplots(figsize=(10, 8))
    grouped = df.groupby('operation_id')
    #colors = plt.cm.get_cmap('tab20', len(grouped))
    x_positions = np.linspace(0, 1, len(grouped))

    for (i, (operation_id, group)), x in zip(enumerate(grouped), x_positions):
        addresses = group['address']
        sizes = group['max_size_per_bank']
        
        ax.errorbar(np.full(len(addresses), x), addresses, yerr=sizes, fmt='o', label=f'Operation {operation_id}', alpha=0.7)

    ax.set_xlabel('Operation ID')
    ax.set_ylabel('Address + Size')
    ax.set_title('L1 Utilization Visualizer')
    ax.grid(True, axis='y')
    ax.set_xticks(x_positions)
    ax.set_xticklabels([str(op_id) for op_id in grouped.groups.keys()])

    plt.show()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot buffers from SQLite file.')
    parser.add_argument('sqlite_file', type=str, help='Path to the SQLite file')
    args = parser.parse_args()
    
    plot_buffers(args.sqlite_file)
