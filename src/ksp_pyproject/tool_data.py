from .kivyschool_data import KivySchoolData

class ToolData:

    kivy_school: KivySchoolData | None

    def __init__(self, data: dict):
        self.kivy_school = (
            KivySchoolData(data["kivy-school"]) if "kivy-school" in data else None
        )