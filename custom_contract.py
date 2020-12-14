state = Variable()
@export
def run(function: str, kwargs: dict):
    if function == "set_var":
        set_state(kwargs)
def set_state(value: dict):
    assert ctx.caller == "sc", "Only the parent contract can call this contract"
    state.set(value)