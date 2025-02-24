from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Related
from models import PatientsModel, ImageSetsModel, ImagesModel, AssessmentsModel

#TODO: FIX Nested types

class PatientsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = PatientsModel
        load_instance = False

    id = auto_field( dump_only=True )
class ImageSetsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = ImageSetsModel
        load_instance = False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    patient = Related()

class ImagesSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = ImagesModel
        load_instance = False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    image_timestamp = auto_field( dump_only=True )
    image_set = auto_field( dump_only=True )

class AssessmentsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = AssessmentsModel
        load_instance = False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    assessment = auto_field( dump_only=True )
    assessment_timestamp = auto_field( dump_only=True )
    image = auto_field( dump_only=True )
