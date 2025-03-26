from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Related
from models import PatientsModel, ImageSetsModel, ImagesModel, AssessmentsModel

#TODO: FIX Nested types to load and dump properly

#* NOTE: The Meta class defines the options/parameters for the schema

class PatientsSchema( SQLAlchemyAutoSchema ):
    """
    Schema for the PatientsModel.

    Handles serialization and deserialization of patient data.
    """
    class Meta:
        model = PatientsModel
        load_instance = False

    id = auto_field( dump_only=True )
class ImageSetsSchema( SQLAlchemyAutoSchema ):
    """
    Schema for the ImageSetsModel.

    Handles serialization and deserialization of image set data, including relationships
    with patients and images.
    """
    class Meta:
        model = ImageSetsModel
        load_instance = False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    patient = Related()

class ImagesSchema( SQLAlchemyAutoSchema ):
    """
    Schema for the ImagesModel.

    Handles serialization and deserialization of image data, including relationships
    with image sets.
    """
    class Meta:
        model = ImagesModel
        load_instance = False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    image_timestamp = auto_field( dump_only=True )
    image_set = auto_field( dump_only=True )

class AssessmentsSchema( SQLAlchemyAutoSchema ):
    """
    Schema for the AssessmentsModel.

    Handles serialization and deserialization of assessment data, including
    relationships with images.
    """
    class Meta:
        model = AssessmentsModel
        load_instance = False
        include_fk = True
        include_relationships = True

    id = auto_field( dump_only=True )
    assessment = auto_field( dump_only=True )
    assessment_timestamp = auto_field( dump_only=True )
    image = auto_field( dump_only=True )
