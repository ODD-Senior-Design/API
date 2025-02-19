from jsf import JSF
import json

SAMPLE_SCHEMA_JSON_PATH = './test/sample_schema.json'
SAMPLE_DATA_JSON_SAVE_PATH = './test/sample_data.json'

with open(SAMPLE_SCHEMA_JSON_PATH, 'r') as f:
    print( json.load( f ) )

jsf = JSF.from_json( SAMPLE_SCHEMA_JSON_PATH )
fake_data = jsf.generate()
print('\n')
print( fake_data )

# Replace sub-oobject ids with super objects id

# Replace image_sets.patient.id with image_sets.patient_id
for set in fake_data["image_sets"]:
    set["patient"]["id"] = set["patient_id"]

for image in fake_data["images"]:
    image["image_set"]["id"] = image["set_id"]
    image["image_set"]["patient"]["id"] = image["image_set"]["patient_id"]

for assesment in fake_data["assessments"]:
    assesment["image"]["id"] = assesment["image_id"]
    assesment["image"]["set_id"] = assesment["set_id"]
    assesment["image"]["image_set"]["id"] = assesment["set_id"]
    assesment["image"]["image_set"]["patient"]["id"] = assesment["image"]["image_set"]["patient_id"]


print('\n')

with open( SAMPLE_DATA_JSON_SAVE_PATH, 'w', encoding='utf-8' ) as f:
    json.dump( fake_data, f, ensure_ascii=False, indent=4 )
