assert False, 'Do not deploy!'

# AMM GOVERNANCE CONTRACT v0.3
# Basic tests have not been completed. DO NOT DEPLOY.
# This code has not been audited.

import rswp

amm_token = rswp

proposal_details = Hash(default_value=0)
total_supply = Variable()
proposal_id = Variable()
state = Hash(default_value=0)

@construct
def seed():
    total_supply.set(0) 
    proposal_id.set(0)
    state['start_time'] = now
    state['start_rate'] = 1
    
    state['minimum_proposal_duration'] = 1 # Number is in days
    state['required_approval_percentage'] = 0.5 # Keep this at 50%, unless there are special circumstances
    state['minimum_quorum'] = 0.05 # Set minimum amount of votes needed

    state['total_token_supply'] = 120000000 # Placeholder value, please double check before deployment
    
@export # this can be made not a public function
def get_timestamp():
    td = now - start_time
    return td.seconds
    
@export
def create_proposal(proposal_type: str, proposal_args: list, description: str, voting_time_in_days: int): #Transfer tokens held by the AMM treasury here
    assert voting_time_in_days >= state['minimum_proposal_duration']
    
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    
    # proposal_details[p_id, "votes"] = 0 # Most likely not needed due to default_value
    
    proposal_details[p_id, "resolved"] = False
    
    proposal_details[p_id, "type"] = proposal_type
    proposal_details[p_id, "args"] = proposal_args
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "duration"] = voting_time_in_days

    return p_id

@export
def vote(p_id: int, amount: float, decision: bool): #Vote here
    assert type(decision) == bool, 'Not a bool!' # TODO: Check this works
    if proposal_details[p_id, ctx.caller, "decision"] != 0: # TODO: Check this works
        assert decision == proposal_details[p_id, ctx.caller, "decision"], 'Previous vote had different decision! Please withdraw previous vote before voting again'
        
    proposal_details[p_id, "votes", decision] += amount
        
    proposal_details[p_id, ctx.caller] += amount
    proposal_details[p_id, ctx.caller, "decision"] = decision
        
    amm_token.transfer_from(to=ctx.this, amount=amount, main_account=ctx.caller)
    
@export
def withdraw_vote(p_id: int): #Vote here
    assert type(proposal_details[p_id, ctx.caller, "decision"]) == bool, 'Not a bool!' # TODO: Check this works
    
    proposal_details[p_id, "votes", proposal_details[p_id, ctx.caller, "decision"]] -= proposal_details[p_id, ctx.caller]
       
    amount = proposal_details[p_id, ctx.caller]
    
    proposal_details[p_id, ctx.caller] = 0
    proposal_details[p_id, ctx.caller, "decision"] = 0
        
    amm_token.transfer(to=ctx.caller, amount=amount)
    
@export
def determine_results(p_id: int): # Vote resolution takes place here
    assert (proposal_details[p_id, "time"] + datetime.timedelta(days=1) * (proposal_details[p_id, "duration"])) <= now, "Proposal not over!" # Checks if proposal has concluded - TODO: Make sure this works
    assert proposal_details[p_id, "resolved"] is not True, "Proposal already resolved" # Checks that the proposal has not been resolved before - can be replaced with `is False`
    
    assert p_id < proposal_id.get() # Checks proposal exists
    
    proposal_details[p_id, "resolved"] = True 
        
    quorum = state['total_token_supply'] - amm_token.balance_of(ctx.this)
    for x in state['deductible_wallets']:
        quorum -= amm_token.balance_of(x)
        
    if proposal_details[p_id, "votes", True] / (proposal_details[p_id, "votes", True] + proposal_details[p_id, "votes", False]) > state['minimum_quorum'] and proposal_details[p_id, "votes", True] >= (quorum * state['minimum_quorum']): #Checks that the approval percentage of the votes has been reached (% of total votes)
        proposal_details[p_id, "result"] = True
        
        if proposal_details[p_id, "type"] == "transfer": # transfer token request
            t_c = importlib.import_module(proposal_details[p_id, "args"][0])
            t_c.transfer(amount=proposal_details[p_id, "args"][1], to=proposal_details[p_id, "args"][2])
            
        elif proposal_details[p_id, "type"] == "approval": # approve token transfer request
            t_c = importlib.import_module(proposal_details[p_id, "args"][0])
            t_c.approve(amount=proposal_details[p_id, "args"][1], to=proposal_details[p_id, "args"][2])
            
        elif proposal_details[p_id, "type"] == "set_internal_state": # Possible TODO: Move this to a seperate proposal type
            state[proposal_details[p_id, "args"][0]] = proposal_details[p_id, "args"][1]
            
        elif proposal_details[p_id, "type"] == "set_external_state":
            contract = importlib.import_module(proposal_details[p_id, "args"][0])
            contract.set_state(key=proposal_details[p_id, "args"][1], new_state=proposal_details[2])
            
        else:
            return True, proposal_details[p_id, "type"]
            
        return True
    else:
        proposal_details[p_id, "result"] = False
        
        return False

@export
def proposal_result(p_id: int): #Get proposal result bool here
    return proposal_details[p_id, "result"]
