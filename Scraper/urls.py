"""
This is meant to make a url_queue for the user
"""

from dataclasses import dataclass
from typing import Optional

from .downloader import Downloader


@dataclass
class User:
    name: Optional[str] = None
    email: Optional[str] = None
    codeforces_handle: Optional[str] = None
    location: Optional[str] = None


def make_url_queue(user: User):
    """
    Go through the user's fields and then based on which one of these exist, prepare a list of urls to get'
    """
    pass
