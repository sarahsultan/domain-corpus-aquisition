from re import search
from query_expansion import expand_query, load_model
from typing import List

from scrape import (
    extract_articles_from_category,
    extract_categories_wikipedia,
    extract_links_multithread,
    search_wikidata_multithread,
    extract_link_from_wikidata,
    extract_text_from_articles_multithreading,
)


def create_dataset(keyword_list: List[str], save_file: str, language: str = "en"):
    try:
        model = load_model(language)
    except:
        model = None
    wikipedia_categories_list = []
    for keyword in keyword_list:
        expanded_keywords = expand_query(keyword, model, language)
        expanded_keywords.extend(keyword)
        wikidata_links = search_wikidata_multithread(expanded_keywords, num_of_results=20, max_threads=10)
        wikipedia_links = extract_links_multithread(
            extract_link_from_wikidata, wikidata_links, max_threads=10, language=language
        )
        wikipedia_categories = extract_links_multithread(
            extract_categories_wikipedia, wikipedia_links, max_threads=10, language=language
        )
        wikipedia_categories_list.extend(wikipedia_categories)

    wikipedia_categories = list(set(wikipedia_categories))
    wikipedia_links = extract_links_multithread(
        extract_articles_from_category, wikipedia_categories, max_threads=10, language=language
    )
    text = extract_text_from_articles_multithreading(wikipedia_links, max_threads=10)
    with open(save_file, "w") as file:
        file.write(text)


if __name__ == "__main__":
    pass
