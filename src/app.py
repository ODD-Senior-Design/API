from os import getenv
from random import randint
from dotenv import load_dotenv
from flask import Flask, Response, request, jsonify, abort
from flask_cors import CORS
from marshmallow import EXCLUDE, ValidationError
from uuid import UUID
from datetime import datetime

from db_handler import DBhandler
from webhook_handler import CameraInterface, AIInterface
from sample_data_generator import DataGenerator
from schemas import PatientsSchema, ImageSetsSchema, ImagesSchema, AssessmentsSchema

app: Flask = Flask( getenv( "APP_NAME" ) or 'API' )
cors: CORS = CORS( app )
debug_mode: bool = getenv( "DEBUG_MODE" ) == '1'
host_address: str = getenv( "HOST_ADDRESS" ) or '0.0.0.0'
bind_port: int = int( getenv( "BIND_PORT" ) or 5000 )
schema_folder_path: str = getenv( "JSON_SCHEMA_FOLDER_PATH" ) or './src/sample-data-schemas'
max_samples: int = int( getenv( "MAX_SAMPLES" )  or '5')
db = DBhandler( getenv( "DB_URI" ) or '', debug=debug_mode )
ci = CameraInterface( getenv( "CAMERA_INTERFACE_URL" ) or '', debug=debug_mode )
ai = AIInterface( getenv( "AI_INTERFACE_URL" ) or '', debug=debug_mode )

@app.route( '/images', methods=['GET'] )
def get_latest_image() -> Response:
    image = db.get_top_entry( table_name='images', order='image_timestamp' )

    if image is None:
        abort( 404, 'No images saved' )

    schema = ImagesSchema()

    return jsonify( schema.dump( image ) )

@app.route( '/images/<uuid:uid>', methods=['GET'] )
def get_image_from_uuid( uid: UUID ) -> Response:
    image = db.get_entry_from_id( uuid=uid, table_name='images' )

    if image is None:
        abort( 404, 'No images with that UUID' )

    schema = ImagesSchema()

    return jsonify( schema.dump( image ) )

@app.route( '/images', methods=['POST'] )
def take_image() -> Response:
    patient_data: dict = request.get_json()

    try:
        schema = PatientsSchema()
        patient_data = schema.load( patient_data )
    except ValidationError as e:
        abort( 400, e.messages )

    image_data = ci.capture_image( payload=patient_data )

    if image_data is None:
        abort( 500, 'Failed to capture image' )

    image_metadata = db.create_entry( data=image_data, table_name='images' )

    if image_metadata is None:
        abort( 500, 'Failed to insert new image entry' )

    return jsonify( image_metadata )

@app.route( '/assessments', methods=['POST'] )
def assess_image() -> Response:
    image_data: dict = request.get_json()
    schema = AssessmentsSchema()

    try:
        image_data = schema.load( image_data )
    except ValidationError as e:
        abort( 400, e.messages )

    assessment_data = ai.analyze_image( image_data ) or { 'assessment': True, 'assessment_timestamp': datetime.now() }

    if assessment_data is None:
        abort( 500, 'Failed to analyze image' )

    assessment_data.update( image_data )
    assessment_data.update( { 'id': 'a6158250-f9cb-1f87-b5bc-a40d93d9d15b' } ) #! TEMPORARY! FOR TESTING ONLY
    assessment_metadata = assessment_data #db.create_entry( data=assessment_data, table_name='assessments' )

    if assessment_metadata is None:
        abort( 500, 'Failed to insert new assessment entry' )

    image_data = db.get_entry_from_id( uuid=image_data.get( 'image_id', '' ), table_name='images' ) or {}

    if image_data == {}:
        abort( 500, 'Failed to retrieve image data' )

    image_data.update( { 'image_set': { 'id': image_data[ 'set_id' ], 'patient_id': image_data[ 'patient_id' ], 'patient': {} } } )
    image_data[ 'image_set' ].update( { 'patient': db.get_entry_from_id( uuid=image_data.get( 'patient_id', '' ), table_name='patients' ) or {} } )

    image_schema = ImagesSchema()

    assessment_metadata['image'] = image_schema.dump( image_data )

    return jsonify( schema.dump( assessment_data ) )

@app.route( '/generate', methods=['GET'] )
def generate__all_sample_data() -> Response:
    datagen = DataGenerator( f'{ schema_folder_path }/all.json', debug_mode | ( getenv( 'SAVE_SAMPLE_DATA_TO_JSON' ) is not None ), getenv( 'SAMPLE_DATA_JSON_SAVE_PATH' ) )
    sample_data = datagen.generate_data()
    if sample_data is None:
        abort( 500, 'Sample data could not be generated' )
    return jsonify( sample_data )

@app.route( '/generate/assessments', methods=['GET'] )
def generate_assessments_sample_data() -> Response:
    num = request.args.get( 'num', randint(1, max_samples), type=int )
    datagen = DataGenerator( f'{ schema_folder_path }/assessments.json' or '', debug_mode | ( getenv( 'SAVE_SAMPLE_DATA_TO_JSON' ) is not None ), getenv( 'SAMPLE_DATA_JSON_SAVE_PATH' ) )
    sample_data = datagen.generate_data( num )
    if sample_data is None:
        abort( 500, 'Sample data could not be generated' )

    return jsonify( sample_data )

@app.route( '/generate/images', methods=['GET'] )
def generate_images_sample_data() -> Response:
    num = request.args.get( 'num', randint(1, max_samples), type=int )
    datagen = DataGenerator( f'{ schema_folder_path }/images.json' or '', debug_mode | ( getenv( 'SAVE_SAMPLE_DATA_TO_JSON' ) is not None ), getenv( 'SAMPLE_DATA_JSON_SAVE_PATH' ) )
    sample_data = datagen.generate_data( num )
    if sample_data is None:
        abort( 500, 'Sample data could not be generated' )

    return jsonify( sample_data )

@app.route( '/generate/sets', methods=['GET'] )
def generate_sets_sample_data() -> Response:
    num = request.args.get( 'num', randint(1, max_samples), type=int )
    datagen = DataGenerator( f'{ schema_folder_path }/sets.json' or '', debug_mode | ( getenv( 'SAVE_SAMPLE_DATA_TO_JSON' ) is not None ), getenv( 'SAMPLE_DATA_JSON_SAVE_PATH' ) )
    sample_data = datagen.generate_data( num )
    if sample_data is None:
        abort( 500, 'Sample data could not be generated' )

    return jsonify( sample_data )

@app.route( '/generate/patients', methods=['GET'] )
def generate_patients_sample_data() -> Response:
    num = request.args.get( 'num', randint(1, max_samples), type=int )
    datagen = DataGenerator( f'{ schema_folder_path }/patients.json' or '', debug_mode | ( getenv( 'SAVE_SAMPLE_DATA_TO_JSON' ) is not None ), getenv( 'SAMPLE_DATA_JSON_SAVE_PATH' ) )
    sample_data = datagen.generate_data( num )
    if sample_data is None:
        abort( 500, 'Sample data could not be generated' )

    return jsonify( sample_data )

@app.errorhandler( 400 )
def bad_request( error_context ): return jsonify( { 'message': f'Bad Request, Additional Info: { error_context.description }' } ), 400

@app.errorhandler( 404 )
def not_found( error_context ): return jsonify( { 'message': f'Object Not Found, Additional Info: { error_context.description }' } ), 404

@app.errorhandler( 500 )
def internal_server_error( error_context ): return jsonify( { 'message': f'Database/Server Error: { error_context.description }' } ), 500

def start_app():
    print( 'Loading .env file if present...' )
    load_dotenv()
    print( 'Starting API...' )
    app.run( debug=debug_mode, host=host_address, port=bind_port )

if __name__ == '__main__':
    start_app()
