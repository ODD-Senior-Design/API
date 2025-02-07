import sqlalchemy as sa
from uuid import UUID
from typing import Optional, List, Dict, Any

class DBhandler():

    def __init__( self, db_uri: str ):

        self.__engine: sa.Engine = sa.create_engine( db_uri )
        self.__metadata = sa.MetaData()
        self.__init_tables()

    def __init_tables( self ):
        self.__tables = [

            sa.Table (

                'patients', self.__metadata,
                sa.Column( 'id', sa.UUID, primary_key=True ),
                sa.Column( 'first_name', sa.String, nullable=False ),
                sa.Column( 'last_name', sa.String, nullable=False )

            ),

            sa.Table (

                'image_sets', self.__metadata,
                sa.Column( 'id', sa.UUID, primary_key=True ),
                sa.Column( 'patient_id', sa.UUID, sa.ForeignKey( 'patients.id' ) )

            ),

            sa.Table (

                'images', self.__metadata,
                sa.Column( 'id', sa.UUID, primary_key=True ),
                sa.Column( 'set_id', sa.UUID, sa.ForeignKey( 'image_sets.id' ) ),
                sa.Column( 'patient_id', sa.UUID, sa.ForeignKey( 'patients.id' ) ),
                sa.Column( 'image_timestamp', sa.String, nullable=False),
                sa.Column( 'uri', sa.String, unique=True, nullable=False )

            ),

            sa.Table (

                'assessments', self.__metadata,
                sa.Column( 'id', sa.UUID, primary_key=True ),
                sa.Column( 'image_id', sa.UUID, sa.ForeignKey( 'images.id' ) ),
                sa.Column( 'set_id', sa.UUID, sa.ForeignKey( 'image_sets.id' ) ),
                sa.Column( 'patient_id', sa.UUID, sa.ForeignKey( 'patients.id' ) ),
                sa.Column( 'assessment_timestamp', sa.String, nullable=False ),
                sa.Column( 'assessment', sa.Integer, nullable=False )

            )

        ]

        self.__metadata.create_all( self.__engine )

    def get_entries_from_id( self, uuid: UUID, table_name: str ) -> Optional[ List[ Dict[ str, Any ] ] ]:
        table: sa.Table = [ t for t in self.__tables if t.name == table_name ][0]
        query = sa.select( '*' ).where( table.c.id == uuid )

        with self.__engine.begin() as conn:
            result = conn.execute( query ).fetchall()
            result = list( map( lambda r: { str( column.name ): getattr( r, column.name ) for column in r.__table__.columns }, result ) ) # Dict expansion to convert the `Row` type to a `Dict` type

        return result or None

    def create_entry( self, data: dict, table_name: str ) -> Optional[ str ]:
        table: sa.Table = [ t for t in self.__tables if t.name == table_name ][0]
        new_entry = table.insert().values( data )

        with self.__engine.begin() as conn:
            result = conn.execute( new_entry ).inserted_primary_key or []

        return result[0] or None
