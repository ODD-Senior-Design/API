import sqlalchemy as sa
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

        query = sa.select( model ).order_by( sa.desc( order ) )

        try:
            with self.__engine.begin() as conn:
                result = conn.execute( query ).fetchone()
                result = result._asdict() if result else None

        except Exception as e:
            print( f'Error occurred while fetching top entry: { e }' )
            return None
    
        return result

    def get_entry_from_id( self, uuid: UUID, table_name: str ) -> Optional[ Dict[ str, Any ] ]:

        model = self.__get_model_from_table_name( table_name )

        if model is None:
            return None

        query = sa.select( model ).where( model.id == str( uuid ) )

        try:
            with self.__engine.begin() as conn:
                result = conn.execute( query ).fetchone()
                result = result._asdict() if result else None

        except Exception as e:
            print( f'Error occurred while fetching entry by ID: { e }' )
            return None

        return result

    def create_entry( self, data: dict, table_name: str ) -> Optional[ Dict[ str, Any ] ]:

        model = self.__get_model_from_table_name( table_name )

        if model is None:
            return None

        new_entry = model( **data )

        try:
            with self.__engine.begin() as conn:
                result = conn.execute( new_entry ).inserted_primary_key or ''
                result = conn.execute( sa.select( model ).where( model.id == str( result ) ) ).fetchone()
                result = result._asdict() if result else None

        except Exception as e:
            print( f'Error occurred while creating entry: {e}' )
            return None

        return result
