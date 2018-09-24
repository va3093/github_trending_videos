from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from github_trending.managers.github_trending import get_trending_repos
from github_trending.managers.instgram import post_trending_repo
from github_trending.database import Database
from github_trending.models.base import Base
from github_trending.models.repo import Repo
from github_trending.logs import configure_logging


configure_logging()

engine = create_engine('sqlite:///repos.db', echo=False)
Base.metadata.create_all(engine)
database = Database(engine=engine)

# for repo in get_trending_repos():
#     try:
#         session = database.generate_session()
#         repo.save(session)
#     except IntegrityError as exc:
#         print(f"Got {exc} but ignoring")

session = database.generate_session()
repos = session.query(Repo).filter(Repo.gif_link.isnot(None))
for repo in repos:
    post_trending_repo(repo)
    repo.posted = True
    repo.save(session)
