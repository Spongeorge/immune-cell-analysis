# ⚙️ Setup

Install requirements:
```shell
pip install -r requirements.txt
```

Initialize SQLite DB:
```shell
python database/create_db.py
```

To run the dashboard locally:
```shell
python -m dashboard.app
```

# 🗂️ DB Schema

EDA of cell-count.csv revealed that no patient corresponded to multiple `projects`, `conditions`, or `treatments`. As a result, bridge tables to handle potential many-to-many relationships were omitted for simplicity.

Although `conditions` and `treatments` could have been represented as a simple string or enum field in the `subjects` table, decoupling these now makes it easier to extend them in the future, without too much additional complexity (e.g. if we wanted to add a 'dosage amount' column to `treatments`).

The `cell_counts` table is also decoupled from `samples` to separate sample metadata from quantitative measurements.
# Code Structure

# Dashboard