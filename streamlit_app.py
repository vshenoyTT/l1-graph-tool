import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import mplcursors

def plot_buffers(sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    
    query = """
    SELECT buffers.operation_id, operations.name as operation_name, buffers.address, buffers.max_size_per_bank
    FROM buffers
    JOIN operations ON buffers.operation_id = operations.operation_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    pivot_df = df.pivot_table(index=['operation_id', 'operation_name'], columns='address', values='max_size_per_bank', fill_value=0)

    pivot_df.index = pivot_df.index.set_levels(
        [pivot_df.index.levels[0], pivot_df.index.levels[1].str[5:]],
        level=['operation_id', 'operation_name']
    )

    chunk_size = 50
    num_chunks = len(pivot_df) // chunk_size + (1 if len(pivot_df) % chunk_size != 0 else 0)

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk_df = pivot_df.iloc[start_idx:end_idx]

        fig, ax = plt.subplots(figsize=(12, 10), dpi=60) 
        bars = chunk_df.plot(kind='bar', stacked=True, ax=ax, alpha=0.7, legend=False)
        
        ax.set_xlabel('Operation ID')
        ax.set_ylabel('L1 Buffer Size')
        ax.set_title(f'L1 Utilization Visualizer (Ops {chunk_df.index[0][0]}-{chunk_df.index[-1][0]})')
        ax.grid(True, axis='y')

        ax.set_xticks(range(len(chunk_df)))  # Set x-ticks for each operation
        ax.set_xticklabels(chunk_df.index.get_level_values('operation_id'), rotation=90)  # Label x-ticks with operation IDs

        fig.tight_layout()

        def make_cursor_callback(local_chunk_df):
            def on_add(sel):
                idx = sel.target.index
                operation_name = local_chunk_df.index[idx][1]
                sel.annotation.set_text(operation_name)
            return on_add

        cursor = mplcursors.cursor(bars, hover=True)
        cursor.connect("add", make_cursor_callback(chunk_df))

        st.pyplot(fig)

        st.write(f"Operations {chunk_df.index[0][0]}-{chunk_df.index[-1][0]}")
        operation_info_df = chunk_df.index.to_frame(index=False)
        operation_info_df.reset_index(drop=True, inplace=True) 
        st.dataframe(operation_info_df, use_container_width=True)

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
