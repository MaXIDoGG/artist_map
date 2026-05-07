class ArtistMapError(Exception):
    pass


class ArtistNotFoundError(ArtistMapError):
    pass


class PathNotFoundError(ArtistMapError):
    pass


class EmptyGraphError(ArtistMapError):
    pass
