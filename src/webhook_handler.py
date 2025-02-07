import requests as req
from typing import Optional, Dict
class camera_interface():
    
    def __init__( self, url ):
        self.__url = url
        
    def capture_image( self, payload: dict, headers: dict = { 'Content-type': 'application/json' } ) -> Optional[ Dict ]:
        # sourcery skip: default-mutable-arg
        resp = req.post( url=self.__url, headers=headers, json=payload )
        
        return resp.json() or None
        
        