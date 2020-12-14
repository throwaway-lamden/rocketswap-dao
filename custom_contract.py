state = Variable()
@export
def set_state(value: str):
    assert ctx.caller == "sc", "Only the parent contract can call this contract"
    state.set(value)