from requests.exceptions import ConnectionError
from todoist_api_python.api import TodoistAPI


class Todoist:
    api_key = ""
    todoist_api = False

    def __init__(self, api_key):
        self.api_key = api_key
        todoist_api = TodoistAPI(self.api_key)

        try:
            print(todoist_api.get_projects())
        except ConnectionError:
            print("Failed to connect to Todoist. Exiting")
            self.todoist_api = False

