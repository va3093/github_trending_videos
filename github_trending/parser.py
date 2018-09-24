import re

from bs4 import BeautifulSoup
from github_trending.models.trending_repo_row_item import (
    TrendingRepoRowItem
)


GITHUB = 'https://github.com'


def trending_repo_rows_items(html_page):
    repos = []

    soup = BeautifulSoup(html_page, "lxml")

    for li in soup.find_all(
            'li', {'class': 'col-12 d-block width-full py-4 border-bottom'}):
        avatar_img = li.find('img', {'class': 'avatar mb-1'})
        if avatar_img:
            avatar = avatar_img['src']

        name_div = li.find('div', {'class': 'd-inline-block col-9 mb-1'})
        name_string = name_div.find('a', href=True)['href']
        # name_string = li.find('span', {'class': 'text-normal'}).string
        owner = name_string.split('/')[1]
        repo = name_string.split('/')[2]
        link = GITHUB + name_string

        meta = li.find('div', {'class': 'f6 text-gray mt-2'})

        if meta:
            stars = li.find(
                'a',
                {
                    'class': 'muted-link d-inline-block mr-3'
                }).text.replace('\n', '').strip(' ')
        else:
            stars = "0"

        description = parser_desc(li.find('div', {'class': 'py-1'}))

        repos.append(TrendingRepoRowItem(
            owner=owner,
            avatar=avatar,
            repo=repo,
            stars=stars,
            description=description,
            link=link
        ))

    return repos


def parser_desc(desc):
    repo_desc = ""

    if desc:
        for each in desc.stripped_strings:
            repo_desc += " " + each

    return repo_desc.lstrip(" ")


class ReadmeParser():

    def __init__(self, *, readme_html):
        self.readme_html = readme_html
        self.soup = BeautifulSoup(readme_html, "lxml")

    def get_absolute_gif_url(self, *, relative_path, repo_link):
        stripped_path = re.findall(r'(master/.*)', relative_path)[0]
        base_url = repo_link.replace(
            'https://github.com',
            'https://raw.githubusercontent.com')
        return f"{base_url}/{stripped_path}"

    def is_relative_link(self, link):
        return not str.startswith(link, 'http')

    def gif_link(self, *, repo_link):
        try:
            gif_link = re.findall(
                r'("[^"]+.gif")',
                self.readme_html)[0].replace(
                    '"', '')
        except IndexError:
            return None
        if not gif_link:
            return None
        if self.is_relative_link(gif_link):
            gif_link = self.get_absolute_gif_url(
                relative_path=gif_link, repo_link=repo_link)
        return gif_link

    def title(self):
        title_tags = [
            self.soup.h1, self.soup.h2, self.soup.h3]
        for tag in title_tags:
            if tag:
                return tag.text
        return ''

    def introduction(self):
        for tag in self.soup.find_all('p'):
            if tag.text:
                return tag.text
        return ''
