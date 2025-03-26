from jsf import JSF
import json
from typing import Optional, Dict, List, Any

class DataGenerator:
    """Generates sample data based on a JSON schema."""
    def __init__( self, json_schema_path, save_as_json=False, json_save_path=None ):
        """Initializes the data generator.

        Args:
            json_schema_path ( str ): Path to the JSON schema file.
            save_as_json ( bool, optional ): Whether to save the generated data as a JSON file. Defaults to False.
            json_save_path ( str, optional ): Path to save the JSON file. If None, defaults to 'generated_data.json'.
        """
        self.__json_schema_path = json_schema_path
        self.__save_as_json = save_as_json
        self.__json_save_path = json_save_path

    def __fix_inconsistencies( self, data: dict ) -> Dict[str, Any]:
        """Fixes inconsistencies in the generated data.

        This method updates nested dictionaries to ensure consistency in IDs across different levels.

        Args:
            data ( dict ): The data dictionary to fix.

        Returns:
            Dict[str, Any]: The fixed data dictionary.
        """
        if data.get( 'image_id' ):
            data[ 'image' ].update( { 'id': data[ 'image_id' ], 'set_id': data[ 'set_id' ], 'patient_id': data[ 'patient_id' ] } )
            data[ 'image' ][ 'image_set' ].update( { 'id': data[ 'set_id' ], 'patient_id': data[ 'patient_id' ] } )
            data[ 'image' ][ 'image_set' ][ 'patient' ][ 'id' ] = data[ 'patient_id' ]

        elif data.get( 'set_id' ):
            data[ 'image_set' ].update( { 'id': data[ 'set_id' ], 'patient_id': data[ 'patient_id' ] } )
            data[ 'image_set' ][ 'patient' ][ 'id' ] = data[ 'patient_id' ]

        elif data.get( 'patient_id' ):
            data[ 'patient' ][ 'id' ] = data[ 'patient_id' ]

        return data.copy()

    def generate_data( self, num=1 ) -> Optional[List[Dict[str, Any]]]:
        """Generates sample data based on the provided JSON schema.

        Args:
            num ( int, optional ): The number of data samples to generate. Defaults to 1.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of generated data samples, or None if an error occurred.
        """
        try:
            jsf = JSF.from_json( self.__json_schema_path )
        except Exception as e:
            print( f'Error occurred while loading JSON schema: {e}' )
            return None

        sample_data = jsf.generate( n=num )
        if num == 1:
            sample_data = [ sample_data ]

        if sample_data[0].get( 'assessments' ):
            for sample in sample_data:
                sample[ 'assessments' ] = [ self.__fix_inconsistencies( a ) for a in sample[ 'assessments' ] ]
                sample[ 'images' ] = [ self.__fix_inconsistencies( i ) for i in sample[ 'images' ] ]
                sample[ 'image_sets' ] = [ self.__fix_inconsistencies( s ) for s in sample[ 'image_sets' ] ]
                sample[ 'patients' ] = [ self.__fix_inconsistencies( p ) for p in sample[ 'patients' ] ]
        else:
            sample_data = [ self.__fix_inconsistencies( d ) for d in sample_data ]

        print( sample_data )

        if self.__save_as_json:
            with open( self.__json_save_path or 'generated_data.json', 'w' ) as f:
                json.dump( sample_data, f, indent=4 )

        return sample_data
