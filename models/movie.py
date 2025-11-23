class Movie:
    def __init__(self, id: str, title: str, genres: str):
        self.id = id
        self.title = title
        self.genres = genres

    def __dict__(self):
        return {
            "id": self.id,
            "title": self.title,
            "genres": self.genres
        }
