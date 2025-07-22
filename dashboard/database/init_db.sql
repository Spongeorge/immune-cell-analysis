-- Drop tables if they exist (for reruns)
-- DROP TABLE IF EXISTS cell_counts;
-- DROP TABLE IF EXISTS samples;
-- DROP TABLE IF EXISTS subjects;
-- DROP TABLE IF EXISTS projects;

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY
);

CREATE TABLE subjects (
    subject_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    condition_id TEXT NOT NULL,
    treatment_id TEXT NOT NULL,
    age INTEGER,
    sex TEXT CHECK(sex IN ('M', 'F')),
    response TEXT CHECK(response IN ('yes', 'no')),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (condition_id) REFERENCES conditions(condition_id),
    FOREIGN KEY (treatment_id) REFERENCES treatments(treatment_id)
);

CREATE TABLE conditions (
    condition_id TEXT PRIMARY KEY,
    condition_name TEXT
);

CREATE TABLE treatments (
    treatment_id TEXT PRIMARY KEY,
    treatment_name TEXT
);

CREATE TABLE samples (
    sample_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE cell_counts (
    sample_id TEXT PRIMARY KEY,
    b_cell INTEGER,
    cd8_t_cell INTEGER,
    cd4_t_cell INTEGER,
    nk_cell INTEGER,
    monocyte INTEGER,
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
);
