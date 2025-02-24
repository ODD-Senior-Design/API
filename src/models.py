from datetime import datetime
from uuid import UUID
from sqlalchemy import ForeignKey, String as id_type
from sqlalchemy.orm import (

    DeclarativeBase,
    backref,
    relationship,
    mapped_column,
    Mapped

)

# pylint: disable=unsubscriptable-object

class _Base( DeclarativeBase ):
    def __getitem__( self, key ):
        return self.__dict__[ key ]

class PatientsModel( _Base ):
    __tablename__ = 'patients'
    id: Mapped[ UUID ] = mapped_column( id_type, primary_key=True )
    first_name: Mapped[ str ] = mapped_column( nullable=False )
    last_name: Mapped[ str ] = mapped_column( nullable=False )

class ImageSetsModel( _Base ):
    __tablename__ = 'image_sets'
    id: Mapped[ UUID ] = mapped_column( id_type, primary_key=True )
    patient_id: Mapped[ UUID ] = mapped_column( ForeignKey( 'patients.id' ) )
    patient: Mapped[ PatientsModel ] = relationship( PatientsModel, backref=backref( 'image_sets', uselist=False ) )

class ImagesModel( _Base ):
    __tablename__ = 'images'
    id: Mapped[ UUID ] = mapped_column( id_type, primary_key=True )
    set_id: Mapped[ UUID ] = mapped_column( ForeignKey( 'image_sets.id' ) )
    patient_id: Mapped[ UUID ] = mapped_column( ForeignKey( 'patients.id' ) )
    image_set: Mapped[ ImageSetsModel ] = relationship( ImageSetsModel, backref=backref( 'images', uselist=False ) )
    image_timestamp: Mapped[ datetime ] = mapped_column( nullable=False )
    uri: Mapped[ str ] = mapped_column( nullable=False, unique=True )

class AssessmentsModel( _Base ):
    __tablename__ = 'assessments'
    id: Mapped[ UUID ] = mapped_column( id_type, primary_key=True )
    image_id: Mapped[ UUID ] = mapped_column( ForeignKey( 'images.id' ) )
    set_id: Mapped[ UUID ] = mapped_column( ForeignKey( 'image_sets.id' ) )
    patient_id: Mapped[ UUID ] = mapped_column( ForeignKey( 'patients.id' ) )
    image: Mapped[ ImagesModel ] = relationship( ImagesModel, backref=backref( 'assessments', uselist=False ) )
    assessment_timestamp: Mapped[ datetime ] = mapped_column( nullable=False )
    assessment: Mapped[ bool ] = mapped_column( nullable=False )
