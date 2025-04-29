from datetime import datetime
from os import getenv
from dotenv import load_dotenv
from jsf import JSF
from faker import Faker
from typing import Dict, Any
import json
import random
import sqlalchemy as sa
from sqlalchemy.orm import Session
import sys
sys.path.insert(0, r'./src/')
from models import PatientsModel, ImagesModel, ImageSetsModel, AssessmentsModel

FAKE_DATA_SCHEMA_JSON_PATH = './src/sample-data-schemas/all.json'
FAKE_DATA_JSON_SAVE_PATH = './test/fake_data.json'
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%f+00:00'
STORE_TO_DB = True
OVERRIDE_DB = True

with open(FAKE_DATA_SCHEMA_JSON_PATH, 'r') as f:
    print( json.load( f ) )

jsf = JSF.from_json( FAKE_DATA_SCHEMA_JSON_PATH )
fake_data = jsf.generate()
print('\n')
print( fake_data )


def fix_sex_field(patients: dict) -> Dict[ str, Any ]:
    patients["sex"] = random.choice(["Male", "Female"])
    return patients.copy()

fake_data[ 'patients' ] = [ fix_sex_field( p ) for p in fake_data[ 'patients' ] ]

def fix_inconsistencies( data: dict ) -> Dict[ str, Any ]:

    faker = Faker()

    if data.get( 'image_id' ):
        data[ 'image' ].update( { 'id': data[ 'image_id' ], 'set_id': data[ 'set_id' ], 'patient_id': data[ 'patient_id' ] } )
        data[ 'image' ][ 'image_set' ].update( { 'id': data[ 'set_id' ], 'patient_id': data[ 'patient_id' ] } )
        data[ 'image' ][ 'image_set' ][ 'patient' ][ 'id' ] = data[ 'patient_id' ]
        data[ 'image' ][ 'image_set' ][ 'patient' ][ 'first_name' ] =  faker.first_name_male() if data[ 'image' ][ 'image_set' ][ 'patient' ][ 'sex' ] == "Male" else faker.first_name_female()

    elif data.get( 'set_id' ):
        data[ 'image_set' ].update( { 'id': data[ 'set_id' ], 'patient_id': data[ 'patient_id' ] } )
        data[ 'image_set' ][ 'patient' ][ 'id' ] = data[ 'patient_id' ]
        data[ 'image_set' ][ 'patient' ][ 'first_name' ] =  faker.first_name_male() if data[ 'image_set' ][ 'patient' ][ 'sex' ] == "Male" else faker.first_name_female()

    elif data.get( 'patient_id' ):
        data[ 'patient' ][ 'id' ] = data[ 'patient_id' ]
        data[ 'patient' ][ 'first_name' ] =  faker.first_name_male() if data[ 'patient' ][ 'sex' ] == "Male" else faker.first_name_female()


    return data.copy()

fake_data[ 'assessments' ] = [ fix_inconsistencies( a ) for a in fake_data[ 'assessments' ] ]
fake_data[ 'images' ] = [ fix_inconsistencies( i ) for i in fake_data[ 'images' ] ]
fake_data[ 'image_sets' ] = [ fix_inconsistencies( s ) for s in fake_data[ 'image_sets' ] ]
fake_data[ 'patients' ] = [ fix_inconsistencies( p ) for p in fake_data[ 'patients' ] ]

print('\n')

with open( FAKE_DATA_JSON_SAVE_PATH, 'w', encoding='utf-8' ) as f:
    json.dump( fake_data, f, ensure_ascii=False, indent=4 )

if not STORE_TO_DB:
    print('No database connection specified. Skipping database operations.')
    exit(0)

print( getenv( 'DB_URI' ) )
engine = sa.create_engine( getenv( 'DB_URI' ) or '' )

if OVERRIDE_DB:
    with Session( engine ) as conn:
        # Delete all data from the database but keep the tables
        conn.execute( sa.delete(PatientsModel) )
        conn.execute( sa.delete(ImageSetsModel) )
        conn.execute( sa.delete(ImagesModel) )
        conn.execute( sa.delete(AssessmentsModel) )
        conn.commit()

def de_onion_dict( collection, popval ):
    outer_values = [ dict(iset) for iset in collection ]
    inner_values = list( map( lambda x: dict(x.pop( popval )), outer_values ) )
    return outer_values, inner_values

insert_patients = [ PatientsModel( **p ) for p in fake_data[ 'patients' ] ]

image_set_values, image_set_patients = de_onion_dict( fake_data[ 'image_sets' ], 'patient' )

insert_image_sets = [ ImageSetsModel( **iset ) for iset in image_set_values ]
insert_patients.extend( PatientsModel( **p ) for p in image_set_patients )

images_values, images_image_sets = de_onion_dict( fake_data[ 'images' ], 'image_set' )
images_image_sets, images_image_set_patients = de_onion_dict( images_image_sets, 'patient' )

for img in images_values:
    img[ 'image_timestamp' ] = datetime.strptime( img[ 'image_timestamp' ], TIMESTAMP_FORMAT )

insert_images = [ ImagesModel( **img ) for img in images_values ]
insert_image_sets.extend( ImageSetsModel( **iset ) for iset in images_image_sets )
insert_patients.extend( PatientsModel( **p ) for p in images_image_set_patients )

assessment_values, assessment_images = de_onion_dict( fake_data[ 'assessments' ], 'image' )
assessment_images, assessment_images_image_sets = de_onion_dict( assessment_images, 'image_set' )
assessment_images_image_sets, assessment_images_image_sets_patients = de_onion_dict( assessment_images_image_sets, 'patient' )

for a in assessment_values:
    a[ 'assessment_timestamp' ] = datetime.strptime( a[ 'assessment_timestamp' ], TIMESTAMP_FORMAT )

for img in assessment_images:
    img[ 'image_timestamp' ] = datetime.strptime( img[ 'image_timestamp' ], TIMESTAMP_FORMAT )

insert_assessments = [ AssessmentsModel( **a ) for a in assessment_values ]
insert_images.extend( ImagesModel( **img ) for img in assessment_images )
insert_image_sets.extend( ImageSetsModel( **iset ) for iset in assessment_images_image_sets )
insert_patients.extend( PatientsModel( **p ) for p in assessment_images_image_sets_patients )

query = sa.select( AssessmentsModel )

with Session(engine) as conn:
    conn.add_all( insert_assessments )
    conn.add_all( insert_images )
    conn.add_all( insert_image_sets )
    conn.add_all( insert_patients )
    conn.commit()

    result = conn.execute( query ).fetchall()
    for r in result:
        print( r._asdict().get( 'AssessmentsModel' ).__dict__ )
        print()

if __name__ == '__main__':
    load_dotenv()
