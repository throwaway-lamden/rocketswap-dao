# Major WIP, only a proof in concept right now
# Do not use as-is

state = Variable()

@export
def run(function: str, kwargs: dict):
    assert ctx.caller == "sc", "Only the parent contract can call this contract"
    
    if function == "set_var":
        set_state(kwargs)
        
def set_state(value: dict):
    state.set(value)
    return True
