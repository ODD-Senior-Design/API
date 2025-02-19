from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import PatientsModel, ImageSetsModel, ImagesModel, AssessmentsModel

class PatientsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = PatientsModel
        load_instance =  False
        include_relationships = True

class ImageSetsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = ImageSetsModel
        load_instance =  False
        include_relationships = True

class ImagesSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = ImagesModel
        load_instance =  False
        include_relationships = True

class AssessmentsSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = AssessmentsModel
        load_instance =  False
        include_relationships = True
