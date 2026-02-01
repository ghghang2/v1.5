import inspect
name="n"
func=lambda: None

for frame in inspect.stack():
    gl=frame.frame.f_globals
    if gl.get("__name__")!="mod":
        gl.setdefault("func", func)
        gl.setdefault("name", name)
        break
