""" Module responsible for interacting with the Github to
fetch and process trending repos
"""
import logging
import requests

from github_trending.models.repo import Repo
from github_trending.parser import (
    trending_repo_rows_items, ReadmeParser)

_logger = logging.getLogger(__name__)
GITHUB = 'https://github.com'
TRENDING_URL = GITHUB + "/trending"
USER_AGENT_BY_MOBILE = (
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36')


def get_trending_html_page(url, timeout=5):
    _logger.info(f"Getting trending repo home page: {url}")
    header = {'User-Agent': USER_AGENT_BY_MOBILE}
    try:
        response = requests.get(url=url, timeout=timeout, headers=header)
    except requests.exceptions.ConnectionError as e:
        return None, False

    return response


def generate_repo_models(row_items):
    headers = {'User-Agent': USER_AGENT_BY_MOBILE}
    repos = []
    for row in row_items:
        readme_res = requests.get(
            row.link + "/blob/master/README.md", headers=headers)
        readme_parser = ReadmeParser(readme_html=readme_res.text)
        gif_link = readme_parser.gif_link(
            repo_link=row.link)
        title = readme_parser.title()
        introduction = readme_parser.introduction()
        if gif_link:
            _logger.info(f"Found gif link: {gif_link} for repo {row.link}")
        repos.append(
            Repo(
                owner=row.owner,
                avatar=row.avatar,
                repo=row.repo,
                stars=row.stars,
                description=row.description,
                link=row.link,
                title=title,
                introduction=introduction,
                gif_link=gif_link
            )
        )
    return repos


def get_trending_repos(opts=None):
    repos = []
    opts = opts or {}

    language = opts.get('language', None)
    since = opts.get('since', None)

    url = TRENDING_URL

    if language:
        url = url + '/' + language

    if since:
        url += '?since={}'.format(since)

    response = get_trending_html_page(url)
    response.raise_for_status()

    row_items = trending_repo_rows_items(response.text)
    repos = generate_repo_models(row_items)

    return repos
