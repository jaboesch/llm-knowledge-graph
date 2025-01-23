import requests
import wikipedia

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

# Using the wikipedia API directly because the library doesn't properly handle dismabiguation pages
def fetch_page_content(query: str):
    try:
        # Perform a search to get the most relevant page
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1,
            "srnamespace": 0,  # Search only in the main content namespace
        }
        search_response = requests.get(WIKIPEDIA_API_URL, params=search_params)
        search_data = search_response.json()

        # Check if search results are empty
        if not search_data["query"]["search"]:
            return {"error": f"No results found for query: {query}"}

        # Get the pageid of the top result
        top_result = search_data["query"]["search"][0]
        pageid = top_result["pageid"]

        # Use the pageid to fetch the content of the page
        page_params = {
            "action": "query",
            "pageids": pageid,
            "prop": "extracts",
            "explaintext": True,
            "format": "json",
        }
        page_response = requests.get(WIKIPEDIA_API_URL, params=page_params)
        page_data = page_response.json()

        # Extract page content
        pages = page_data["query"]["pages"]
        page = pages[str(pageid)]  # Access the page using its ID

        # Return the title and full content
        return page["extract"]

    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def fetch_top_k_summaries(query, k=5):
    try:
        search_results = wikipedia.search(query)

        if not search_results:
            return []

        summaries = []
        for title in search_results[:k]:
            try:
                summary = wikipedia.summary(title, sentences=2)
                summaries.append({"title": title, "summary": summary})
            except wikipedia.exceptions.PageError:
                summaries.append({"title": title, "summary": "Page not found."})
            except Exception as e:
                summaries.append({"title": title, "summary": f"An error occurred: {e}"})

        return summaries
    except Exception as e:
        return f"An error occurred during search: {e}"


class InputManager:
    def __init__(self, topic: str):
        # TODO: Implement logic to use top-k summaries and allow LLM to pick relevant articles
        self.input = fetch_page_content(topic)
