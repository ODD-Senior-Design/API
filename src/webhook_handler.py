import requests as req
from typing import Optional, Dict, Any

class CameraInterface:
    """Interface for interacting with a camera service.

    Provides methods for capturing images and retrieving stream URLs.
    """

    def __init__( self, url: str, timeout: int = 10, debug: bool = False ):
        """Initializes the CameraInterface.

        Args:
            url ( str ): The base URL of the camera service.
            timeout ( int, optional ): Request timeout in seconds. Defaults to 10.
            debug ( bool, optional ): Enables debug logging. Defaults to False.
        """
        self.__url = url
        self.__timeout = timeout
        self.__debug = debug

    def capture_image( self, payload: dict, headers: Optional[Dict] = None ) -> Optional[Dict[str, Any]]:
        """Captures an image using the camera service.

        Args:
            payload ( dict ): The request payload for capturing the image.
            headers ( Optional[Dict], optional ): Request headers. Defaults to None.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the camera service, or None if an error occurred.
        """
        # sourcery skip: default-mutable-arg
        default_header = { 'Content-type': 'application/json' }

        try:
            resp = req.post( url=f'{ self.__url }/capture', headers=headers or default_header, json=payload, timeout=self.__timeout )

        except req.exceptions.RequestException as e:
            if self.__debug: print( f'Error occurred while capturing image:\n\n{ e }\n\n' )
            return None

        return resp.json()

    def get_stream_url( self ) -> Optional[str]:
        """Retrieves the stream URL from the camera service.

        Returns:
            Optional[str]: The stream URL, or None if an error occurred.
        """
        try:
            resp = req.get( url=f'{ self.__url }/stream', timeout=self.__timeout )

        except req.exceptions.RequestException as e:
            if self.__debug: print( f'Error occurred while getting stream URL:\n\n{ e }\n\n' )
            return None

        return resp.json().get( 'stream_url' )

class AnalyzerInterface:
    """Interface for interacting with an image analysis service.

    Provides a method for analyzing images.
    """

    def __init__( self, url: str, timeout: int = 10, debug: bool = False ):
        """Initializes the AnalyzerInterface.

        Args:
            url ( str ): The URL of the image analysis service.
            timeout ( int, optional ): Request timeout in seconds. Defaults to 10.
            debug ( bool, optional ): Enables debug logging. Defaults to False.
        """
        self.__url = url
        self.__timeout = timeout
        self.__debug = debug

    def analyze_image( self, payload: dict, headers: Optional[Dict] = None ) -> Optional[Dict[str, Any]]:
        """Analyzes an image using the analysis service.

        Args:
            payload ( dict ): The request payload for analyzing the image.
            headers ( Optional[Dict], optional ): Request headers. Defaults to None.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the analysis service, or None if an error occurred.
        """
        # sourcery skip: default-mutable-arg
        default_header = { 'Content-type': 'application/json' }

        try:
            resp = req.post( url=self.__url, headers=headers or default_header, json=payload, timeout=self.__timeout )

        except req.exceptions.RequestException as e:
            if self.__debug: print( f'Error occurred while analyzing image:\n\n{ e }\n\n' )
            return None

        return resp.json()
