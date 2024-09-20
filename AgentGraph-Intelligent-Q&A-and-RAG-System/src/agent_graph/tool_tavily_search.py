from langchain_community.tools.tavily_search import TavilySearchResults


def load_tavily_search_tool(tavily_search_max_results: int):
    """
    This function initializes a Tavily search tool, which performs searches and returns results
    based on user queries. The `max_results` parameter controls how many search results are
    retrieved for each query.

    Args:
        tavily_search_max_results (int): The maximum number of search results to return for each query.

    Returns:
        TavilySearchResults: A configured instance of the Tavily search tool with the specified `max_results`.
    """
    return TavilySearchResults(max_results=tavily_search_max_results)
