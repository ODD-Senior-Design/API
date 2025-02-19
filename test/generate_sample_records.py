from jsf import JSF
import json

NUM_TO_GENERATE = 1
SAMPLE_SCHEMA_JSON_PATH = './test/sample_schema.json'
SAMPLE_DATA_JSON_SAVE_PATH = './test/sample_data.json'

with open(SAMPLE_SCHEMA_JSON_PATH) as f:
    print( json.load( f ) )

jsf = JSF.from_json( SAMPLE_SCHEMA_JSON_PATH )
fake_data = jsf.generate( NUM_TO_GENERATE )
print('\n')
print( fake_data )

with open( SAMPLE_DATA_JSON_SAVE_PATH, 'w', encoding='utf-8' ) as f:
    json.dump( fake_data, f, ensure_ascii=False, indent=4 )
