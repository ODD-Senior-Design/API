import requests as req
from typing import Optional, Dict, Any

class CameraInterface():

    def __init__( self, url: str, timeout: int = 10, debug: bool = False ):
        self.__url = url
        self.__timeout = timeout
        self.__debug = debug

    def capture_image( self, payload: dict, headers: Optional[ Dict ] = None ) -> Optional[ Dict[ str, Any ] ]:
        # sourcery skip: default-mutable-arg
        default_header = { 'Content-type': 'application/json' }

        try:
            resp = req.post( url=f'{ self.__url }/capture', headers=headers or default_header, json=payload, timeout=self.__timeout )

        except req.exceptions.RequestException as e:
            if self.__debug: print( f'Error occurred while capturing image:\n\n{ e }\n\n' )
            return None

        return resp.json()
    
    def get_stream_url( self ) -> Optional[ str ]:
        try:
            resp = req.get( url=f'{ self.__url }/stream', timeout=self.__timeout )

        except req.exceptions.RequestException as e:
            if self.__debug: print( f'Error occurred while getting stream URL:\n\n{ e }\n\n' )
            return None

        return resp.json().get( 'stream_url' )

class AIInterface():

    def __init__( self, url: str, timeout: int = 10, debug: bool = False ):
        self.__url = url
        self.__timeout = timeout
        self.__debug = debug

    def analyze_image( self, payload: dict, headers: Optional[ Dict ] = None ) -> Optional[ Dict[ str, Any ] ]:
        # sourcery skip: default-mutable-arg
        default_header = { 'Content-type': 'application/json' }

        try:
            resp = req.post( url=self.__url, headers=headers or default_header, json=payload, timeout=self.__timeout )

        except req.exceptions.RequestException as e:
            if self.__debug: print( f'Error occurred while analyzing image:\n\n{ e }\n\n' )
            return None

        return resp.json()
