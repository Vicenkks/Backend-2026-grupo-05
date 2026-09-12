from app.domain.space import Space

class SpaceRepository:
    def __init__(self):
        self.spaces: dict[str, Space] = {}


    def add(self, space:Space) -> Space:
        self.spaces[space.spaceId] = space
        return space

    def get_by_id(self, spaceId:str) -> Space| None:
        return self.spaces.get(spaceId)

    def get_all(self) -> list[Space]:
        return list(self.spaces.values())

    def delete(self, space:Space) -> bool:
        return self.spaces.pop(space.spaceId, None) is not None