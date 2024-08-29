import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import mplcursors

st.set_page_config(layout="wide")

def plot_buffers(sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    
    query = """
    SELECT buffers.operation_id, operations.name as operation_name, buffers.address, buffers.max_size_per_bank
    FROM buffers
    JOIN operations ON buffers.operation_id = operations.operation_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['end_address'] = df['address'] + df['max_size_per_bank']
    
    # Sort the dataframe by address to ensure proper plotting order
    df = df.sort_values(by='address')

    fig, ax = plt.subplots(figsize=(12, 200), dpi=60)

    # Plot each buffer as a horizontal bar at its address
    for _, row in df.iterrows():
        ax.barh(row['operation_id'], row['max_size_per_bank'], left=row['address'], height=0.8, label=row['operation_name'])
    
    ax.set_xlabel('Address')
    ax.set_ylabel('Operation ID')
    ax.set_title('L1 Buffer Utilization')
    
    ax.grid(True, axis='x')

    # Clamp y-axis range to the min and max operation ID
    min_op_id = df['operation_id'].min()
    max_op_id = df['operation_id'].max()
    ax.set_ylim(min_op_id - 1, max_op_id + 1)

    # Set x-ticks as required
    minTick = df['address'].min() - 100000
    maxTick = df['end_address'].max()
    x_ticks = range(minTick, maxTick + 1, 100000)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f'{(x // 1000)}k' for x in x_ticks])

    # Adding a cursor to display operation names
    def make_cursor_callback(local_df):
        def on_add(sel):
            idx = sel.target.index
            operation_name = local_df.iloc[idx]['operation_name']
            sel.annotation.set_text(operation_name)
        return on_add

    cursor = mplcursors.cursor(ax.containers, hover=True)
    cursor.connect("add", make_cursor_callback(df))

    st.pyplot(fig)
    
    # Display the DataFrame for additional insight
    st.write(f"Operation buffers address range: {df['address'].min()} to {df['end_address'].max()}")
    st.write(f"Operations with buffers ID range: {df['operation_id'].min()} to {df['operation_id'].max()}")
    df_sorted = df.sort_values(by='operation_id', ascending=True)
    st.dataframe(df_sorted[['operation_id', 'operation_name', 'address', 'max_size_per_bank']], use_container_width=True)


def main():
    hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
    '''
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    st.title("Tenstorrent L1 Utilization Graph")

    uploaded_file = st.file_uploader("Choose a SQLite file", type="sqlite")

    if uploaded_file is not None:
        with open("temp_sqlite_file.sqlite", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        plot_buffers("temp_sqlite_file.sqlite")

if __name__ == "__main__":
    main()
