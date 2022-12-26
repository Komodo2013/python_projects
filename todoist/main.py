import plyer

import todoist
import canvas
import gui


todoist_api_key = "c0c9886ed9370c334b7df1329ffd02024d1d2b01"
canvas_api_key = "2974~Ymjt5hMUEQ5Lay30hzwKSc3o4UPnY6vjhFgz3RSRUAPiMtEWacW6wAIqYV81FX6Y"
todo = todoist.Todoist(todoist_api_key)
canvas = canvas.Canvas(canvas_api_key)

canvas_header = {"Authorization": "Bearer " + canvas_api_key}

gui = gui.GUIApp()

# plyer.notification.notify(title="Test", message="Hello there", )

if __name__ == "__main__":
    gui.run()
