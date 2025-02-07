DROP TABLE IF EXISTS images;
CREATE TABLE images (

    id TEXT NOT NULL PRIMARY KEY,
    set_id TEXT NOT NULL,
    patient_first TEXT NOT NULL,
    patient_last TEXT NOT NULL,
    uri TEXT NOT NULL UNIQUE

);

DROP TABLE IF EXISTS image_sets;
CREATE TABLE image_sets (
    
    id TEXT NOT NULL PRIMARY KEY,
    patient_first TEXT NOT NULL,
    patient_last TEXT NOT NULL

);

