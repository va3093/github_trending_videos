from sqlalchemy import Column, String, Boolean

from .base import Base

from github_trending.database import (
    CRUDMixin, Auditable, SurrogatePK,
    OutputMixin
)


class Repo(Base, CRUDMixin, Auditable, SurrogatePK, OutputMixin):
    __tablename__ = 'repo'

    owner = Column(String)
    avatar = Column(String)
    repo = Column(String)
    stars = Column(String)
    description = Column(String)
    link = Column(String, unique=True)
    gif_link = Column(String)
    posted = Column(Boolean)
    title = Column(String)
    introduction = Column(String)
