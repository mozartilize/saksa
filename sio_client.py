import socketio

sio = socketio.Client()


@sio.event
def message(data):
    print(f"I received a message! {data}")


sio.connect("http://localhost:8000", auth={"username": "hatv"})
