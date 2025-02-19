DROP TABLE IF EXISTS patients;
CREATE TABLE patients (

    id TEXT NOT NULL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL

);


DROP TABLE IF EXISTS image_sets;
CREATE TABLE image_sets (
    
    id TEXT NOT NULL PRIMARY KEY,
    patient_id TEXT NOT NULL,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id)

);

DROP TABLE IF EXISTS images;
CREATE TABLE images (

    id TEXT NOT NULL PRIMARY KEY,
    set_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    image_timestamp TEXT NOT NULL,
    uri TEXT NOT NULL UNIQUE,

    FOREIGN KEY (set_id) REFERENCES image_sets(id),
    FOREIGN KEY (patient_id) REFERENCES patients(id)

);

DROP TABLE IF EXISTS assessments;
CREATE TABLE assessments (

    id TEXT NOT NULL PRIMARY KEY,
    image_id TEXT NOT NULL,
    set_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    assessment_timestamp TEXT NOT NULL,
    assessment BOOLEAN NOT NULL CHECK ( assessment IN (0, 1) ),

    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (set_id) REFERENCES image_sets(id)

);
