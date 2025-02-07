DROP TABLE IF EXISTS Images;
CREATE TABLE Images (

    id TEXT NOT NULL PRIMARY KEY,
    patient_first TEXT NOT NULL,
    patient_last TEXT NOT NULL,
    uri TEXT NOT NULL UNIQUE

);