import sqlalchemy as sa
from uuid import UUID
from typing import Optional, Tuple, Any

class DBhandler():

    def __init__( self, db_uri: str ):
        
        self.__engine: sa.Engine = sa.create_engine( db_uri )
        self.__metadata = sa.MetaData()
        self.__init_tables()

    def __init_tables( self ):
        self.__tables = [
            
            sa.Table (
                'images', self.__metadata,
                sa.Column( 'id', sa.UUID, primary_key=True ),
                sa.Column( 'patient_first', sa.String ),
                sa.Column( 'patient_last', sa.String ),
                sa.Column( 'uri', sa.String, unique=True )
            )

        ]

        self.__metadata.create_all( self.__engine )

    def get_file_uri_from_uuid( self, uuid: UUID, table_name: str ) -> Optional[ Tuple[ Any ] ]:
        table: sa.Table = [ t for t in self.__tables if t.name == table_name ][0]
        query = sa.select( table.c.uri ).where( table.c.id == uuid )

        with self.__engine.begin() as conn:
            result = conn.execute( query ).fetchone() or []

        return result[0] or None

    def create_entry( self, data: dict, table_name: str ) -> Optional[ str ]:
        table: sa.Table = [t for t in self.__tables if t.name == table_name][0]
        new_entry = table.insert().values( data )

        with self.__engine.begin() as conn:
            result = conn.execute( new_entry ).inserted_primary_key or []

        return result[0] or None
