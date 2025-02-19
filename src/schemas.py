from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models import PatientsModel, ImageSetsModel, ImagesModel, AssessmentsModel

class PatientsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = PatientsModel
        load_instance =  False

    id = auto_field( dump_only=True )

class ImageSetsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = ImageSetsModel
        load_instance =  False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    patient_id = auto_field( dump_only=True )

class ImagesSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = ImagesModel
        load_instance =  False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    set_id = auto_field( dump_only=True )

class AssessmentsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = AssessmentsModel
        load_instance = False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    image_id = auto_field( dump_only=True )
    set_id = auto_field( dump_only=True )
