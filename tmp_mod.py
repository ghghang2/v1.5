import inspect

name="myname"
func=lambda: None

for frame in inspect.stack():
    gl=frame.frame.f_globals
    if gl.get("__name__")!="tmp_mod":
        gl.setdefault("func", func)
        gl.setdefault("name", name)
        break
