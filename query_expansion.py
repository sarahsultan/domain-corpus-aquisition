from typing import List
from multi_rake import Rake
import logging
from gensim.models import fasttext
from definitions import FASTTEXT_MODELS, LANGUAGES
from scrape import create_session, extract_link_from_wikidata, search_wikidata, extract_text_wikipedia


def load_model(language: str = "en") -> fasttext.FastTextKeyedVectors or None:
    """Loads a FastText model for a given language if it exists.

    Args:
        language (str, optional): Language of the model to load. Defaults to "en".

    Returns:
        fasttext.FastTextKeyedVectors: FastText model in gensim
    """
    if language not in LANGUAGES:
        logging.warning("Language is not supported.")
        return None
    try:
        model = fasttext.load_facebook_vectors(FASTTEXT_MODELS + "cc." + language + ".300.bin")
    except FileNotFoundError:
        logging.warning(f"{FASTTEXT_MODELS}cc.{language}.300.bin does not exist.")
        return None
    return model


def extract_keywords_from_text(text: str, num_keywords: int, language: str = "en") -> List[str]:
    """Extract keywords from given text with the RAKE algorithm.

    Args:
        text (str): Text to use the RAKE algorithm on

    Returns:
        List[str]: List of keywords
    """
    rake = Rake(language_code=language)
    keywords = rake.apply(text)
    new_keywords = [keyword[0] for keyword in keywords]
    if num_keywords < len(keywords):
        new_keywords = new_keywords[:num_keywords]
    return new_keywords


def get_most_similar_words(keyword: str, model: fasttext.FastTextKeyedVectors, num_words: int = 5) -> List[str]:
    """Get most similar words for a given keyword.

    Args:
        keyword (str): Keyword.
        model (fasttext.FastTextKeyedVectors): FastText model to use.
        num_words (int, optional): Number of words to consider. Defaults to 5.

    Returns:
        List[str]: List of most similar words.
    """
    most_similar = model.most_similar(positive=keyword, topn=num_words)
    most_similar_words = [word[0] for word in most_similar]
    return most_similar_words


def expand_query(
    keyword: str,
    model: fasttext.FastTextKeyedVectors,
    language: str = "en",
) -> List[str]:
    """Expand the search query for a given keyword.

    Args:
        keyword (str): Keyword to expand.
        language (str): Language of the keyword.
        model (fasttext.FastTextKeyedVectors): FastText model to use.

    Returns:
        List[str]: List of new keywords generated for the given keyword
    """
    new_keywords_list = []
    session = create_session()
    wikidata_search = search_wikidata(keyword, session, num_of_results=1)
    article = extract_link_from_wikidata(wikidata_search[0], session)
    text = extract_text_wikipedia(article[0], session)
    new_keywords_list.extend(extract_keywords_from_text(text, 10, language)[:])
    if model is not None:
        new_keywords_list.extend(get_most_similar_words(keyword, model))
    return new_keywords_list


if __name__ == "__main__":
    pass
