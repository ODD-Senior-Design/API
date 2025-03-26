from os import getenv
from random import randint
from typing import Any
from dotenv import load_dotenv
from flask import Flask, Response, request, jsonify, abort
from flask_cors import CORS
from marshmallow import ValidationError
from uuid import UUID

from db_handler import DBhandler
from webhook_handler import CameraInterface, AIInterface
from sample_data_generator import DataGenerator
from schemas import ImageSetsSchema, PatientsSchema, ImagesSchema, AssessmentsSchema

app: Flask = Flask( getenv( "APP_NAME" ) or 'API' )
cors: CORS = CORS( app )
debug_mode: bool = getenv( "DEBUG_MODE" ) == '1'
host_address: str = getenv( "HOST_ADDRESS" ) or '0.0.0.0'
bind_port: int = int( getenv( "BIND_PORT" ) or 5000 )
schema_folder_path: str = getenv( "JSON_SCHEMA_FOLDER_PATH" ) or './src/sample-data-schemas'
max_samples: int = int( getenv( "MAX_SAMPLES" )  or '5')
datetime_format: str = getenv( "DATETIME_FORMAT" ) or '%Y-%m-%dT%H:%M:%S'
db = DBhandler( getenv( "DB_URI" ) or '', debug=debug_mode )
ci = CameraInterface( getenv( "CAMERA_INTERFACE_URL" ) or '', debug=debug_mode )
ai = AIInterface( getenv( "AI_INTERFACE_URL" ) or '', debug=debug_mode )

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

@app.route( '/stream', methods=['GET'] )
def get_stream_url() -> Response:
    camera_stream_url = ci.get_stream_url()

    if camera_stream_url is None:
        abort( 500, 'Failed to get camera stream URL' )

    return jsonify( { 'stream_url': camera_stream_url } )

@app.route( '/patients', methods=['POST'] )
def add_patient() -> Response:
    patient_data: dict = request.get_json()
    try:
        schema = PatientsSchema()
        patient_data = schema.load( patient_data )
    except ValidationError as e:
        abort( 400, e.messages )

    patient_metadata = db.create_entry( data=patient_data, table_name='patients' )

    if patient_metadata is None:
        abort( 500, 'Failed to insert new patient entry' )

    schema = PatientsSchema()

    return jsonify( schema.dump( patient_metadata ) )

@app.route( '/image_sets', methods=['POST'] )
def add_image_set() -> Response:
    ids: dict = request.get_json()
    try:
        schema = ImageSetsSchema()
        ids = schema.load( ids )
    except ValidationError as e:
        abort( 400, e.messages )

    image_set_metadata = db.create_entry( data=ids, table_name='image_sets' )

    if image_set_metadata is None:
        abort( 500, 'Failed to insert new image set entry' )

    schema = ImageSetsSchema()

    return jsonify( schema.dump( image_set_metadata ) )

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

    image_data.update( patient_data )

    image_metadata = db.create_entry( data=image_data, table_name='images' )

    if image_metadata is None:
        abort( 500, 'Failed to insert new image entry' )

    schema = ImagesSchema()

    return jsonify( schema.dump( image_metadata ) )

@app.route( '/assessments', methods=['POST'] )
def assess_image() -> Response:
    ids: dict[ str, Any ] = request.get_json()
    schema = AssessmentsSchema()

    try:
        ids = schema.load( ids )
    except ValidationError as e:
        abort( 400, e.messages )

    assessment_data = ai.analyze_image( ids )

    if assessment_data is None:
        abort( 500, 'Failed to analyze image' )

    assessment_data.update( ids )

    assessment_data = db.create_entry( data=assessment_data, table_name='assessments' )

    if assessment_data is None:
        abort( 500, 'Failed to insert new assessment entry' )

    return jsonify( schema.dump( assessment_data ) )

@app.route( '/<table_name>', methods=['GET'] )
def get_table_entries( table_name: str ) -> Response:
    entries = db.get_all_entries( table_name=table_name )

    if entries is None:
        abort( 404, f"Table '{ table_name }' does not exist." )

    schema = PatientsSchema( many=True )
    match table_name:
        case 'patients':
            schema = PatientsSchema( many=True )
        case 'image_sets':
            schema = ImageSetsSchema( many=True )
        case 'images':
            schema = ImagesSchema( many=True )
        case 'assessments':
            schema = AssessmentsSchema( many=True )

    return jsonify( schema.dump( entries ) )

@app.route( '/<table_name>/<uuid:uid>', methods=['GET'] )
def get_table_entry_from_id( table_name: str, uid: UUID ) -> Response:
    table_model = db.get_model_from_table_name( table_name=table_name )

    if table_model is None:
        abort( 404, f"Table '{ table_name }' does not exist." )

    entry = db.get_entry_from_id( uuid=uid, table_name=table_name )

    if entry is None:
        abort( 404, f"'No { table_name } with that UUID" )

    schema = PatientsSchema()
    match table_name:
        case 'patients':
            schema = PatientsSchema()
        case 'image_sets':
            schema = ImageSetsSchema()
        case 'images':
            schema = ImagesSchema()
        case 'assessments':
            schema = AssessmentsSchema()

    return jsonify( schema.dump( entry ) )


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
