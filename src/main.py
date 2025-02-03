import pandas as pd
from flask import Flask, Response, jsonify, abort
from uuid import UUID
from db_handler import DBhandler as db
import os

app: Flask = Flask('API') 

@app.route('/panoramas/<uuid:id>', methods=['GET'])
def get_panorama_uri_from_uuid( id: UUID ) -> Response:
    panorama_uri: str = db.get_file_uri_from_uuid( id, 'panorama')
    
    if panorama_uri is None:
        abort( 404 )
        
    return jsonify( { "panorama": panorama_uri } )

@app.route('/panoramas', methods=['POST'])
def create_panorama() -> Response:
    

@app.errorhandler( 404 )
def not_found( error ): return jsonify( error='Object Not Found' ), 404

@app.errorhandler( 500 )
def internal_server_error( error ): return jsonify( error='Server Error' ), 500

if __name__ == '__main__':
    print( 'Starting API...' )
    app.run( debug= os.getenv( "DEBUG_MODE" ) is not None )
