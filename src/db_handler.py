import contextlib
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Session
import secrets
from uuid import UUID
from typing import Optional, List, Dict, Any
from models import PatientsModel, ImageSetsModel, ImagesModel, AssessmentsModel

class DBhandler:
    """Handles database interactions for various models."""

    def __init__( self, db_uri: str, debug: bool, datetime_format: str ):
        """Initializes the database handler.

        Args:
            db_uri ( str ): The database connection URI.
            debug ( bool ): Whether to enable debug mode for the database engine.
        """
        self.__engine: sa.Engine = sa.create_engine( db_uri, echo=debug )
        self.__datetime_format = datetime_format

    def get_model_from_table_name( self, table_name: str ) -> Optional[Any]:
        """Retrieves the SQLAlchemy model associated with a given table name.

        Args:
            table_name ( str ): The name of the table.

        Returns:
            Optional[Any]: The SQLAlchemy model if found, None otherwise.
        """
        return {
            'patients': PatientsModel,
            'image_sets': ImageSetsModel,
            'images': ImagesModel,
            'assessments': AssessmentsModel
        }.get( table_name )

    def get_all_entries( self, table_name: str ) -> Optional[List[Dict[str, Any]]]:
        """Retrieves all entries from a given table.

        Args:
            table_name ( str ): The name of the table.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of dictionaries representing the entries, or None if an error occurs.
        """

        model = self.get_model_from_table_name( table_name )

        if model is None:
            return None

        query = sa.select( model )

        try:
            with self.__engine.begin() as conn:
                result = conn.execute( query ).fetchall()
                result = [ r._asdict() for r in result ]

        except Exception as e:
            print( f'Error occurred while fetching all entries: { e }' )
            return None

        return result

    def get_top_entry( self, table_name: str, order='id' ) -> Optional[ Dict[ str, Any ] ]:
        """Retrieves the top entry from a given table, ordered by a specified column.

        Args:
            table_name ( str ): The name of the table.
            order ( str, optional ): The column to order by. Defaults to 'id'.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the top entry, or None if an error occurs or no entries exist.
        """

        model = self.get_model_from_table_name( table_name )

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

    def get_entry_from_id( self, uuid: UUID, table_name: str ) -> Optional[Dict[str, Any]]:
        """Retrieves an entry from a given table based on its UUID.

        Args:
            uuid ( UUID ): The UUID of the entry.
            table_name ( str ): The name of the table.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the entry, or None if an error occurs or no entry is found.
        """

        model = self.get_model_from_table_name( table_name )

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

        print( result )
        return result

    def create_entry( self, data: dict, table_name: str ) -> Optional[Dict[str, Any]]:
        """Creates a new entry in a given table.

        Args:
            data ( dict ): A dictionary containing the data for the new entry.
            table_name ( str ): The name of the table.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the created entry, or None if an error occurs.
        """

        model = self.get_model_from_table_name( table_name )

        if model is None:
            return None

        new_entry = model( **data )
        if not new_entry.id:
            uid = UUID( hex=secrets.token_hex( 16 ) )

            new_entry.id = str( uid )

        with contextlib.suppress(AttributeError):
            new_entry.image_timestamp = datetime.strptime( new_entry.image_timestamp, self.__datetime_format )
            new_entry.assessment_timestamp = datetime.strptime( new_entry.assessment_timestamp, self.__datetime_format )

        try:
            with Session( self.__engine ) as conn:
                conn.add( new_entry )
                conn.commit()
                result = conn.execute( sa.select( model ).where( model.id == str( new_entry.id ) ) ).fetchone()
                result = [{column.name: getattr(row, column.name) for column in model.__table__.columns} for row in result][0] if result else None

        except Exception as e:
            print( f'Error occurred while creating entry: {e}' )
            return None

        print( f'Created entry:\n{ result }' )
        return result

    def delete_entry_from_id( self, uuid: UUID, table_name: str ) -> Optional[ Dict[str, Any] ]:
        """Deletes an entry from a given table based on its UUID.

        Args:
            uuid ( UUID ): The UUID of the entry to delete.
            table_name ( str ): The name of the table.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the deleted entry, or None if an error occurs or no entry is found.
        """
        model = self.get_model_from_table_name( table_name )

        if model is None:
            return None

        try:
            with Session( self.__engine ) as conn:
                result = conn.execute( sa.delete( model ).where( model.id == str( uuid ) ).returning(*model.__table__.columns) ).fetchone()
                conn.commit()
                result = {column.name: getattr(result, column.name) for column in model.__table__.columns} if result else None
        except Exception as e:
            print(f'Error occurred while deleting entry: {e}')
            return None

        print( f'Deleted entry:\n{ result }' )
        return result


    # TODO: Implement function to get all data linked to a specific patient ID
    def get_all_data_from_patient_id( self, patient_id: UUID, table_name: str ) -> Optional[Dict[str, Any]]:
        """Retrieves all entries from a given table linked to a specific patient ID.

        Args:
            patient_id ( UUID ): The UUID of the patient.
            table_name ( str ): The name of the table.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of dictionaries representing the linked entries, or None if an error occurs.
        """
        pass
