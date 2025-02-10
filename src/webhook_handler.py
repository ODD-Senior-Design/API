import requests as req
from typing import Optional, Dict

class CameraInterface():

    def __init__( self, url: str, timeout: int = 10, debug: bool = False ):
        self.__url = url
        self.__timeout = timeout
        self.__debug = debug

    def capture_image( self, payload: dict, headers: Optional[ Dict ] = None ) -> Optional[ Dict ]:
        # sourcery skip: default-mutable-arg
        default_header = { 'Content-type': 'application/json' }

        try:
            resp = req.post( url=self.__url, headers=headers or default_header, json=payload, timeout=self.__timeout )

        except req.exceptions.RequestException as e:
            if self.__debug: print( f'Error occurred while capturing image: {e}' )
            return None

        return resp.json()
