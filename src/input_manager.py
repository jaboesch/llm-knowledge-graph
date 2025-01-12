class InputManager:
    def __init__(self):
        article_paths = [
            "./data/harry_potter_full_article.txt",
        ]
        with open(article_paths[0], "r") as file:
            text_content = file.read()
        self.input = text_content
