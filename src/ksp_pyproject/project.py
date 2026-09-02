

class Project:
    name: str

    def __init__(self, data: dict):
        self.name = data["name"]