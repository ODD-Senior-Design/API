from jsf import JSF
import json
from typing import Optional, Dict, Any

class DataGenerator():
    def __init__( self, json_schema_path, save_as_json=False, json_save_path=None ):
        self.__json_schema_path = json_schema_path
        self.__save_as_json = save_as_json
        self.__json_save_path = json_save_path
        
    def __fix_inconsistencies( self, data: dict ) -> Dict[ str, Any ]:
        for set in data[ 'image_sets' ]:
            set[ 'patient' ][ 'id' ] = set[ 'patient_id' ]

        for image in data[ 'images' ]:
            image[ 'image_set' ][ 'id' ] = image[ 'set_id' ]
            image[ 'image_set' ][ 'patient_id' ] = image[ 'patient_id' ]
            image[ 'image_set' ][ 'patient' ][ 'id' ] = image[ 'image_set' ][ 'patient_id' ]

        for assessment in data[ 'assessments' ]:
            assessment[ 'image' ][ 'id' ] = assessment[ 'image_id' ]
            assessment[ 'image' ][ 'set_id' ] = assessment[ 'set_id' ]
            assessment[ 'image' ][ 'patient_id' ] = assessment[ 'patient_id' ]
            assessment[ 'image' ][ 'image_set' ][ 'id' ] = assessment[ 'set_id' ]
            assessment[ 'image' ][ 'image_set' ][ 'patient_id' ] = assessment[ 'patient_id' ]
            assessment[ 'image' ][ 'image_set' ][ 'patient' ][ 'id' ] = assessment[ 'patient_id' ]
            
        return data.copy()

        
    def generate_data( self, num=1 ) -> Optional[ Dict[ str, Any ] ]:
        try: 
            jsf = JSF.from_json( self.__json_schema_path )
        except Exception as e:
            print( f'Error occurred while loading JSON schema: {e}' )
            return None
        
        sample_data = jsf.generate( num )
        self.__fix_inconsistencies( sample_data )
        print(sample_data)
        
        if self.__save_as_json:
            with open( self.__json_save_path or 'generated_data.json', 'w' ) as f:
                json.dump( sample_data, f, indent=4 )
                
        return sample_data