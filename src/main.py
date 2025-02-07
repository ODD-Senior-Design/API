from os import getenv
from typing import Optional, Tuple, Any
from flask import Flask, Response, request, jsonify, abort
from uuid import UUID
from db_handler import DBhandler

app: Flask = Flask( getenv( "APP_NAME" ) or 'API' )
db = DBhandler( getenv( "DB_URI" ) or '' )
debug_mode: bool = getenv( "DEBUG_MODE" ) == '1'

@app.route( '/images/<uuid:id>', methods=['GET'] )
def get_image_uri_from_uuid( id: UUID ) -> Response:
    image_uri: Optional[Tuple[str]] = db.get_file_uri_from_uuid( id, 'images' )

    if image_uri is None:
        abort( 404 )

    return jsonify( image_uri )

@app.route( '/images', methods=['POST'] )
def take_image() -> Response:
    image_data: dict = request.get_json()

    image_id: Optional[str] = db.create_entry( data=image_data, table_name='images' )

    if image_id is None:
        abort( 500 )

    return jsonify( { "image_id": image_id } )

@app.errorhandler( 404 )
def not_found( error ): return jsonify( error='Object Not Found' ), 404

@app.errorhandler( 500 )
def internal_server_error( error ): return jsonify( error='Database/Server Error' ), 500

if __name__ == '__main__':
    print( 'Starting API...' )
    app.run( debug=debug_mode )
    
