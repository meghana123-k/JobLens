CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,

    title VARCHAR(255) NOT NULL,

    company_id INTEGER REFERENCES companies(id),

    location VARCHAR(255),

    salary_min INTEGER,

    salary_max INTEGER,

    experience_years INTEGER,

    job_type VARCHAR(50),

    source VARCHAR(100),

    posted_date DATE,

    job_url TEXT UNIQUE,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL
);
CREATE TABLE job_skills (
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,

    PRIMARY KEY (job_id, skill_id)
);
CREATE TABLE etl_logs (
    id SERIAL PRIMARY KEY,

    source_name VARCHAR(100),

    records_processed INTEGER,

    status VARCHAR(50),

    execution_time FLOAT,

    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_jobs_source
ON jobs(source);

CREATE INDEX idx_jobs_posted_date
ON jobs(posted_date);

CREATE INDEX idx_jobs_company
ON jobs(company_id);

CREATE INDEX idx_skills_name
ON skills(skill_name);