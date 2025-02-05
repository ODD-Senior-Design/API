
import sqlalchemy as sa

from typing import Optional, Tuple, Any

class DBhandler():

    def __init__( self, db_uri: str ):
        self.__engine = sa.create_engine( db_uri )
        self.__metadata = sa.MetaData()
        self.__init_tables()

    def __init_tables( self ):
        self.__panoramas = sa.Table(
            'panoramas', self.__metadata,
            sa.Column( 'id', sa.UUID, primary_key=True ),
            sa.Column( 'filename', sa.String, unique=True ),
            sa.Column( 'uri', sa.String )
        )

        self.__metadata.create_all( self.__engine )

    def get_file_uri_from_uuid( self, uuid ) -> Optional[ Any ]:
        query = sa.select( self.__panoramas.c.uri ).where( self.__panoramas.c.id == uuid )

        with self.__engine.begin() as conn:
            result = conn.execute( query ).fetchone() or []

        return result[0]

    def insert_panorama( self, data: dict ) -> Optional[ str ]:
        new_panorama = self.__panoramas.insert().values(
            uuid=sa.func.uuid_generate_v4(),
            filename='panorama.jpg',
            uri='panorama.jpg'
        )

        with self.__engine.begin() as conn:
            result = conn.execute( new_panorama ).inserted_primary_key or []

        return result[0] or None
