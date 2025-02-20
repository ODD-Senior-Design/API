from datetime import datetime
from os import getenv
from dotenv import load_dotenv
from jsf import JSF
import json
import sqlalchemy as sa
from sqlalchemy.orm import Session
import sys
sys.path.insert(0, r'./src/')
from models import PatientsModel, ImagesModel, ImageSetsModel, AssessmentsModel

SAMPLE_SCHEMA_JSON_PATH = './test/sample_schema.json'
SAMPLE_DATA_JSON_SAVE_PATH = './test/sample_data.json'
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
OVERRIDE_DB = True

with open(SAMPLE_SCHEMA_JSON_PATH, 'r') as f:
    print( json.load( f ) )

jsf = JSF.from_json( SAMPLE_SCHEMA_JSON_PATH )
fake_data = jsf.generate()
print('\n')
print( fake_data )

# Replace sub-oobject ids with super objects id

# Replace image_sets.patient.id with image_sets.patient_id
for set in fake_data[ 'image_sets' ]:
    set[ 'patient' ][ 'id' ] = set[ 'patient_id' ]

for image in fake_data[ 'images' ]:
    image[ 'image_set' ][ 'id' ] = image[ 'set_id' ]
    image[ 'image_set' ][ 'patient_id' ] = image[ 'patient_id' ]
    image[ 'image_set' ][ 'patient' ][ 'id' ] = image[ 'image_set' ][ 'patient_id' ]

for assessment in fake_data[ 'assessments' ]:
    assessment[ 'image' ][ 'id' ] = assessment[ 'image_id' ]
    assessment[ 'image' ][ 'set_id' ] = assessment[ 'set_id' ]
    assessment[ 'image' ][ 'set_id' ] = assessment[ 'patient_id' ]
    assessment[ 'image' ][ 'image_set' ][ 'id' ] = assessment[ 'set_id' ]
    assessment[ 'image' ][ 'image_set' ][ 'patient_id' ] = assessment[ 'patient_id' ]
    assessment[ 'image' ][ 'image_set' ][ 'patient' ][ 'id' ] = assessment[ 'patient_id' ]

print('\n')

with open( SAMPLE_DATA_JSON_SAVE_PATH, 'w', encoding='utf-8' ) as f:
    json.dump( fake_data, f, ensure_ascii=False, indent=4 )

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
