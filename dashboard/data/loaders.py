import pandas as pd
import sqlite3
from typing import Tuple


def get_frequency_table(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query("""
        SELECT 
            sample_id,
            b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
        FROM samples
        JOIN cell_counts USING(sample_id)
        WHERE sample_type = 'PBMC'
    """, conn)

    melted = df.melt(id_vars=['sample_id'], var_name='population', value_name='count')
    totals = melted.groupby('sample_id')['count'].sum().reset_index(name='total_count')
    summary = melted.merge(totals, on='sample_id')
    summary['percentage'] = (summary['count'] / summary['total_count']) * 100
    summary['percentage'] = summary['percentage'].apply(lambda x: round(x, 4))
    summary = summary.sort_values(by='sample_id')
    summary = summary[['sample_id', 'total_count', 'population', 'count', 'percentage']].rename(
        columns={'sample_id': 'sample'})

    return summary


def get_responder_data(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query("""
        SELECT sample_id, response, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
        FROM samples
        JOIN subjects USING(subject_id)
        JOIN cell_counts USING(sample_id)
        WHERE sample_type = 'PBMC' AND condition_id = 'melanoma' AND treatment_id = 'miraclib'
    """, conn)

    melted = df.melt(id_vars=['sample_id', 'response'], var_name='population', value_name='count')
    totals = melted.groupby('sample_id')['count'].sum().reset_index(name='total_count')
    summary = melted.merge(totals, on='sample_id')
    summary['percentage'] = (summary['count'] / summary['total_count']) * 100
    return summary


def get_baseline_summary(conn: sqlite3.Connection) -> Tuple[pd.DataFrame]:
    df = pd.read_sql_query("""
        SELECT sample_id, project_id, subject_id, response, sex
        FROM samples
        JOIN subjects USING(subject_id)
        WHERE sample_type = 'PBMC' AND time_from_treatment_start = 0 AND condition_id = 'melanoma' AND treatment_id = 'miraclib'
    """, conn)

    project_counts = df.groupby('project_id').size().reset_index(name='num_samples')
    response_counts = df.groupby('response')['subject_id'].nunique().reset_index(name='num_subjects')
    sex_counts = df.groupby('sex')['subject_id'].nunique().reset_index(name='num_subjects')

    return df, project_counts, response_counts, sex_counts
