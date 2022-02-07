import requests as r
import re
import bs4 as bs
from typing import List
from fake_useragent import FakeUserAgent
from definitions import WIKIDATA, WIKIDATA_PAGE_NUMBER, WIKIDATA_RESULT_PER_PAGE, WIKIDATA_SEARCH, WIKIPEDIA
import concurrent.futures


def create_user_agent() -> str:
    """Creates a random user agent string.

    Returns:
        str: User agent string
    """
    user_agent = FakeUserAgent()
    return str(user_agent.random)


def create_session() -> r.Session:
    """Creates a requests session object with a random user agent string.

    Returns:
        r.Session: Created requests session object
    """
    user_agent = create_user_agent()
    session = r.Session()
    session.headers.update({"User-Agent": user_agent})
    return session


def create_sessions(num_sessions: int) -> List[r.Session]:
    """Creates a list of requests session objects with different random user agent strings.

    Args:
        num_sessions (int): Number of sessions to create

    Returns:
        List[r.Session]: List of requests session objects
    """
    sessions = []
    for i in range(num_sessions):
        temp_session = create_session
        sessions.append(temp_session)
    return sessions


def search_wikidata(search_term: str, session: r.Session, num_of_results: int = 100) -> List[str]:
    """Searches wikidata with the given searchterm and returns a list of wikidata item links.

    Args:
        search_term (str): Search term to use.
        session (r.Session): requests.Session for HTTP GET requests.
        num_of_results (int, optional): Number of wikidata items to use. Defaults to 100.

    Returns:
        List[str]: List of wikidata links (https://www.wikidata.org/wiki/Q + Itemnumber)
    """
    search_url = (
        WIKIDATA + WIKIDATA_SEARCH + search_term + WIKIDATA_PAGE_NUMBER + WIKIDATA_RESULT_PER_PAGE + str(num_of_results)
    )
    request = session.get(url=search_url)
    soup = bs.BeautifulSoup(request.content, "lxml")
    search_results = soup.find_all("a", href=re.compile("/wiki/Q"))
    search_results_enitities = [str(link.get("href")) for link in search_results]
    search_results_enitities = [WIKIDATA + item for item in search_results_enitities]
    return search_results_enitities


def search_wikidata_multithread(
    search_term_list: List[str], num_of_results: int = 10, max_threads: int = 10
) -> List[str]:
    """Searches wikidata with the given searchterm and returns the wikidata items

    Args:
        search_term (str): Search term to use.
        num_of_results (int, optional): Number of wikidata items to use. Defaults to 100.
        max_threads (int, optinal): Maximal number of threads. Defaults to 10.

    Returns:
        List[str]: List of wikidata links (https://www.wikidata.org/wiki/Q + Itemnumber)
    """
    session = create_session()
    entity_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(search_term_list), max_threads)) as executor:
        extracted_entities = [
            executor.submit(search_wikidata, search_term_list[i], session, num_of_results)
            for i in range(len(search_term_list))
        ]
        for task in concurrent.futures.as_completed(extracted_entities):
            entity_list.extend(task.result())
    return entity_list


def extract_link_from_wikidata(wikidata_url: str, session: r.Session, language: str = "en") -> List[str]:
    """Extracts the wikipedia link from wikidata item.

    Args:
        wikidata_url (str): URL for wikidata item (https://www.wikidata.org/wiki/Q + Itemnumber)
        session (r.Session): requests.Session for HTTP GET requests.

    Returns:
        List[str]: List of wikipedia links
    """
    request = session.get(url=wikidata_url)
    soup = bs.BeautifulSoup(request.content, "lxml")
    wikipedia_urls = soup.find("div", {"data-wb-sitelinks-group": "wikipedia"}).find_all(
        "a", href=re.compile(f"https://{language}.wikipedia")
    )
    wikipedia_urls = [str(link.get("href")) for link in wikipedia_urls]
    return wikipedia_urls


def extract_categories_wikipedia(article_url: str, session: r.Session, language: str = "en") -> List[str]:
    """Extract the category from a wikipedia article.

    Args:
        article_url (str): URL for wikipedia article
        session (r.Session): requests.Session for HTTP GET requests.
        language (str):

    Returns:
        List[str]: Category of wikipedia article
    """
    request = session.get(url=article_url)
    soup = bs.BeautifulSoup(request.content, "lxml")
    categories = soup.find("div", {"class": "mw-normal-catlinks"}).find_all("a", href=re.compile("/wiki/"))
    categories = ["https://" + language + WIKIPEDIA + str(link.get("href")) for link in categories]
    return categories[1:]


def extract_articles_from_category(category_url: str, session: r.Session, language: str = "en") -> List[str]:
    """Extract all wikipedia articles from a category.

    Args:
        category_url (str): URL of wikipedia category.
        session (r.Session): requests.Session for HTTP GET requests.

    Returns:
        List[str]: Wikipedia articles in category
    """
    request = session.get(url=category_url)
    soup = bs.BeautifulSoup(request.content, "lxml")
    pages = soup.find("div", {"id": "mw-pages"}).find_all("a", href=re.compile("/wiki/"))
    pages = ["https://" + language + WIKIPEDIA + str(link.get("href")) for link in pages]
    return pages[1:]


def extract_links_multithread(
    extraction_function, url_list: str, max_threads: int = 10, language: str = "en"
) -> List[str]:
    """Extracts all links from the list of urls with the extraction function.

    Args:
        extraction_function (): Function to use for extraction.
        url_list (str): List of urls.
        max_threads (int, optional): Max number of threads. Defaults to 10.

    Returns:
        List[str]: Extracted links.
    """
    session = create_session()
    link_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(url_list), max_threads)) as executor:
        extracted_texts = [
            executor.submit(extraction_function, url_list[i], session, language) for i in range(len(url_list))
        ]
        for task in concurrent.futures.as_completed(extracted_texts):
            link_list.extend(task.result())
    return link_list


def extract_text_wikipedia(wikipedia_url: str, session: r.Session) -> str:
    """Extract article text from wikipedia.

    Args:
        url (str): URL of wikipedia article.
        session (r.Session): requests.Session for HTTP GET requests.

    Returns:
        str: Text from wikipedia article
    """
    request = session.get(url=wikipedia_url)
    soup = bs.BeautifulSoup(request.content, "lxml")
    text = soup.find_all("p")
    text = [t.text.strip() for t in text]
    text = "".join(text)
    cleaned_text = clean_text(text)
    return cleaned_text


def clean_text(text: str) -> str:
    """Clean the given string.

    Args:
        text (str): Text that needs to be cleaned.

    Returns:
        str: Cleaned text.
    """
    output_string_01 = re.sub("\\[[0-9]*[a-z]*\\]", "", text)
    output_string_02 = re.sub("\\xa0", "", output_string_01)
    output_string_03 = re.sub("\\n | \\'", "", output_string_02)
    output_string_04 = re.sub(r"\\", "", output_string_03)
    return output_string_04


def extract_text_from_articles(wikipedia_article_list: List[str], session: r.Session) -> str:
    """Extract the text from the given wikipedia articles.

    Args:
        pages_list (List[str]): List of wikipedia article urls.
        session (r.Session): requests.Session for HTTP GET requests.

    Returns:
        str: Extracted text from the wikipedia articles.
    """
    text = ""
    for article in wikipedia_article_list:
        text_extracted = extract_text_wikipedia(article, session)
        text = " ".join([text, text_extracted])
    return text


def extract_text_from_articles_multithreading(wikipedia_article_list: List[str], max_threads: int = 10) -> str:
    """Extract the text from the given articles.

    Args:
        wikipedia_article_list (List[str]): List of wikipedia article urls.
        max_threads (int, optional): Max number of threads. Defaults to 10.

    Returns:
        str: Raw text from the wikipedia articles.
    """
    session = create_session()
    text = ""
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(wikipedia_article_list), max_threads)) as executor:
        extracted_texts = [
            executor.submit(extract_text_wikipedia, wikipedia_article_list[i], session)
            for i in range(len(wikipedia_article_list))
        ]
        for task in concurrent.futures.as_completed(extracted_texts):
            extracted_text = task.result()
            text = "".join([text, extracted_text])
    return text


if __name__ == "__main__":
    pass
