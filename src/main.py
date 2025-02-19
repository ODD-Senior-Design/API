from os import getenv
from flask import Flask, Response, request, jsonify, abort
from marshmallow import ValidationError
from uuid import UUID
from db_handler import DBhandler
from webhook_handler import CameraInterface
from schemas import PatientsSchema, ImageSetsSchema, ImagesSchema, AssessmentsSchema

app: Flask = Flask( getenv( "APP_NAME" ) or 'API' )
debug_mode: bool = getenv( "DEBUG_MODE" ) == '1'
db = DBhandler( getenv( "DB_URI" ) or '', debug=debug_mode )
ci = CameraInterface( getenv( "CAMERA_INTERFACE_URL" ) or '', debug=debug_mode )

@app.route( '/images/<uuid:id>', methods=['GET'] )
def get_image_uri_from_uuid( id: UUID ) -> Response:
    image_entries = db.get_entries_from_id( id, 'images' )

    if image_entries is None:
        abort( 404 )

    if len( image_entries ) > 1:
        abort( 500, 'Duplicate uuids found' )

    image_uri = image_entries[0].get( 'uri' )

    if image_uri is None:
        abort( 404, 'No image URI found' )

    return jsonify( image_uri )

@app.route( '/images', methods=['POST'] )
def take_image() -> Response:
    image_data: dict = request.get_json()

    # TODO: Payload validation

    resp = ci.capture_image( payload=image_data )

    if resp is None:
        abort( 500, 'Failed to capture image' )

    image_data['uri'] = resp.get( 'uri' )

    image_id = db.create_entry( data=image_data, table_name='images' )

    if image_id is None:
        abort( 500, 'No id recieved for new image' )

    return jsonify( { "id": image_id } )

@app.errorhandler( 404 )
def not_found( error_context ): return jsonify( { 'message': f'Object Not Found, Additional Info: { error_context.description }' } ), 404

@app.errorhandler( 500 )
def internal_server_error( error_context ): return jsonify( { 'message': f'Database/Server Error: { error_context.description }' } ), 500

if __name__ == '__main__':
    print( 'Starting API...' )
    app.run( debug=debug_mode )
