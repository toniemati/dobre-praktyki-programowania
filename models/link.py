class Link:
    def __init__(self, id: str, imdbId: str, tmdbId: str):
        self.id = id
        self.imdbId = imdbId
        self.tmdbId = tmdbId

    def __dict__(self):
        return {
            "id": self.id,
            "imdbId": self.imdbId,
            "tmdbId": self.tmdbId
        }
