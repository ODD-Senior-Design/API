import sqlalchemy as sa
from sqlalchemy import desc
from uuid import UUID
from typing import Optional, List, Dict, Any
from models import PatientsModel, ImageSetsModel, ImagesModel, AssessmentsModel

class DBhandler():

    def __init__( self, db_uri: str, debug: bool ):

        self.__engine: sa.Engine = sa.create_engine( db_uri, echo=debug )
    def __get_model_from_table_name( self, table_name: str ) -> Optional[ Any ]:
        return {
            'patients': PatientsModel,
            'image_sets': ImageSetsModel,
            'images': ImagesModel,
            'assessments': AssessmentsModel
        }.get( table_name )

    def get_top_entry( self, table_name: str, order='id' ) -> Optional[ Dict[ str, Any ] ]:

        model = self.__get_model_from_table_name( table_name )

        if model is None:
            return None


        query = sa.select( model ).order_by( desc( order ) )

        with self.__engine.begin() as conn:
            result = conn.execute( query ).fetchone()
            result = result._asdict() if result else None

        return result

    def get_entries_from_id( self, uuid: UUID, table_name: str ) -> Optional[ List[ Dict[ str, Any ] ] ]:

        model = self.__get_model_from_table_name( table_name )

        if model is None:
            return None

        query = sa.select( model ).where( model.id == str(uuid) )

        with self.__engine.begin() as conn:
            result = conn.execute( query ).fetchall()
            result = list( map( lambda r: r._asdict(), result ) ) # Dict expansion to convert the `Row` type to a `Dict` type

        return result or None

    def create_entry( self, data: dict, table_name: str ) -> Optional[ str ]:

        model = self.__get_model_from_table_name( table_name )

        if model is None:
            return None

        new_entry = model( **data )

        with self.__engine.begin() as conn:
            result = conn.execute( new_entry ).inserted_primary_key or []

        return result[0] or None
