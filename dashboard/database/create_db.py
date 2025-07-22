import sqlite3
import pandas as pd
import argparse
import os


def create_db(args):
    if args.drop and os.path.exists(args.db_path):
        os.remove(args.db_path)
        print(f"Dropped existing database: {args.db_path}")

    df = pd.read_csv(args.csv_path)

    df['b_cell'] = df['b_cell'].astype(int)
    df['cd8_t_cell'] = df['cd8_t_cell'].astype(int)
    df['cd4_t_cell'] = df['cd4_t_cell'].astype(int)
    df['nk_cell'] = df['nk_cell'].astype(int)
    df['monocyte'] = df['monocyte'].astype(int)

    conn = sqlite3.connect(args.db_path)
    cur = conn.cursor()

    with open(args.schema_path, 'r') as f:
        cur.executescript(f.read())

    projects = df['project'].unique()
    cur.executemany("INSERT INTO projects (project_id) VALUES (?)", [(p,) for p in projects])

    conditions = df['condition'].unique()
    cur.executemany("INSERT INTO conditions (condition_id) VALUES (?)", [(c,) for c in conditions])

    treatments = df['treatment'].unique()
    cur.executemany("INSERT INTO treatments (treatment_id) VALUES (?)", [(t,) for t in treatments])

    subjects = df[['subject', 'project', 'age', 'sex', 'condition', 'treatment', 'response']].drop_duplicates()
    subject_records = subjects.to_records(index=False)
    cur.executemany("""
        INSERT INTO subjects (subject_id, project_id, age, sex, condition_id, treatment_id, response)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, subject_records)

    samples = df[['sample', 'subject', 'sample_type', 'time_from_treatment_start']].rename(
        columns={'sample': 'sample_id', 'subject': 'subject_id'})
    samples.to_sql('samples', conn, if_exists="replace", index=False)

    cell_counts = df[['sample', 'b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']].rename(
        columns={'sample': 'sample_id'})

    cell_counts.to_sql("cell_counts", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

    print(f"Data loaded successfully into {args.db_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Populates the SQLite database from a csv file.')
    parser.add_argument('--csv-path', type=str, default='data/cell-count.csv')
    parser.add_argument('--schema-path', type=str, default='database/init_db.sql')
    parser.add_argument('--db-path', type=str, default='database/trial_data.db')
    parser.add_argument('--drop', type=bool, default=True)

    create_db(parser.parse_args())
