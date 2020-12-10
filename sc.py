#AMM GOVERNANCE CONTRACT v0.1.2 WITH INTEGRATED TOKEN
#No tests have been run, so do not deploy this in production at this time
#This code has not been audited. Proceed at your own risk

import amm_token
sig = Hash(default_value=False)
proposal_details = Hash()
number_of_sig = Variable()
proposal_id = Variable()
minimum_proposal_duration = Variable()
required_approval_percentage = Variable()
finished_proposals = Variable()
active_contract = Variable()
minimum_quorum = Variable()
sign_transaction_contract = Variable()
status = Hash()
balances = Hash(default_value=0)
misc = Hash()
@construct
def seed():
    supply = 10000000 #Set total supply
    balances["wallet1"] = supply #Change this to change initial distribution
    number_of_sig.set(supply) 
    proposal_id.set(0)
    minimum_proposal_duration.set(0) #Number is in days
    required_approval_percentage.set(0.5) #Keep this at 50%, unless there are special circumstances
    minimum_quorum.set(0.01) #Set minimum amount of votes needed
    sign_transaction_contract.set() #This contract should have the governance contract set as owner. This does not need to be set at contract creation, but it is an option to allow future extensibility 
    finished_proposals.set([-1]) #Probably not needed
@export
def create_transfer_proposal(token_contract: str, amount: float, to: str, description: str, voting_time_in_days: int): #Transfer tokens held by the AMM treasury here
    assert voting_time_in_days >= minimum_proposal_duration.get()
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "token_contract"] = token_contract
    proposal_details[p_id, "amount"] = amount
    proposal_details[p_id, "reciever"] = to
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "transfer"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def create_approval_proposal(token_contract: str, amount: float, to: str, description: str, voting_time_in_days: int): #Approve the transfer of tokens held by the AMM treasury here
    assert voting_time_in_days >= minimum_proposal_duration.get()
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "token_contract"] = token_contract
    proposal_details[p_id, "amount"] = amount
    proposal_details[p_id, "reciever"] = to
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "approval"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def vote(p_id: int, result: bool): #Vote here
    sig[p_id, ctx.caller] = result
    try:
        proposal_details[p_id, "voters"].append(ctx.caller)
    except AttributeError:
        proposal_details[p_id, "voters"] = [ctx.caller]
@export
def determine_results(p_id: int): #Vote resolution takes place here
    assert (proposal_details[p_id, "time"] + datetime.timedelta(days=1) * (proposal_details[p_id, "duration"])) <= now, "Proposal not over!" #Checks if proposal has concluded
    proposals_finished = finished_proposals.get() 
    for x in proposals_finished:
        assert p_id != x #Checks that the proposal has not been resolved before (to prevent double spends)
    proposals_finished.append(p_id) #Adds the proposal to the list of resolved proposals
    finished_proposals.set(proposals_finished)
    approvals = 0
    total_votes = 0
    for x in proposal_details[p_id, "voters"]:
        if sig[p_id, x] == True:
            approvals += balances[x]
        total_votes += balances[x]
    quorum = number_of_sig.get() - balances[ctx.this] 
    if approvals < (quorum * minimum_quorum.get()): #Checks that the minimum approval percentage has been reached (quorum)
        return False
    if approvals / total_votes >= required_approval_percentage.get(): #Checks that the approval percentage of the votes has been reached (% of total votes)
        if proposal_details[p_id, "type"] == "transfer": 
            t_c = importlib.import_module(proposal_details[p_id, "token_contract"])
            t_c.transfer(proposal_details[p_id, "amount"], proposal_details[p_id, "reciever"])
        elif proposal_details[p_id, "type"] == "approval":
            t_c = importlib.import_module(proposal_details[p_id, "token_contract"])
            t_c.approve(proposal_details[p_id, "amount"], proposal_details[p_id, "reciever"])
        elif proposal_details[p_id, "type"] == "change_approval_percentage":
            required_approval_percentage.set(proposal_details[p_id, "amount"])
        elif proposal_details[p_id, "type"] == "change_minimum_duration":
            minimum_proposal_duration.set(proposal_details[p_id, "amount"])
        elif proposal_details[p_id, "type"] == "change_active_contract":
            active_contract.set(proposal_details[p_id, "contract"])
        elif proposal_details[p_id, "type"] == "sign_custom_transaction":
            contract = importlib.import_module(proposal_details[p_id, "contract"])
            contract.run(proposal_details[p_id, "function"], proposal_details[p_id, "kwargs"])
        elif proposal_details[p_id, "type"] == "mint":
            balances[proposal_details[p_id, "reciever"]] += proposal_details[p_id, "amount"]
            number_of_sig.set(number_of_sig.get() + proposal_details[p_id, "amount"])
        elif proposal_details[p_id, "type"] == "set_state":
            misc[proposal_details[p_id, "key"]] = proposal_details[p_id, "new_state"]
        status[p_id] = True
        return True
    else:
        status[p_id] = False
        return False
@export
def change_approval_percentage(new_percentage: float, description: str, voting_time_in_days: int): 
    assert voting_time_in_days >= minimum_proposal_duration.get()
    assert new_percentage <= 1
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "amount"] = new_percentage
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "change_approval_percentage"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def create_signalling_vote(action: int, description: str, voting_time_in_days: int):
    assert voting_time_in_days >= minimum_proposal_duration.get()
    assert new_minimum_amount <= 365
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "action"] = action
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "create_signalling_vote"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def change_minimum_duration(new_minimum_amount: int, description: str, voting_time_in_days: int):
    assert voting_time_in_days >= minimum_proposal_duration.get()
    assert new_minimum_amount <= 365
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "amount"] = new_minimum_amount
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "change_minimum_duration"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def change_active_contract(new_contract: str, description: str, voting_time_in_days: int):
    assert voting_time_in_days >= minimum_proposal_duration.get()
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "contract"] = new_contract
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "change_active_contract"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def sign_custom_transaction(contract: str, function: str, kwargs: dict, description: str, voting_time_in_days: int): #For future extensibility. It is highly recommended that any contract put in the contract field has its owner set to the governance contract 
    assert voting_time_in_days >= minimum_proposal_duration.get()
    assert new_minimum_amount <= 365
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "contract"] = contract
    proposal_details[p_id, "function"] = function
    proposal_details[p_id, "kwargs"] = kwargs
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "sign_custom_transaction"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def create_mint_proposal(amount: float, to: str, description: str, voting_time_in_days: int): #Mint tokens. Warning: Dangerous, and can lead to the takeover of the SC
    assert voting_time_in_days >= minimum_proposal_duration.get()
    assert voting_time_in_days > 7, "Minting has a set minimum length of 7 days"
    assert amount > 0
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "amount"] = amount
    proposal_details[p_id, "reciever"] = to
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "mint"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export
def set_state(new_state: str, key: list, description: str, voting_time_in_days: int): #Set state here. For future extensibility
    assert voting_time_in_days >= minimum_proposal_duration.get()
    p_id = proposal_id.get()
    proposal_id.set(p_id + 1)
    proposal_details[p_id, "state"] = new_state
    proposal_details[p_id, "key"] = key
    proposal_details[p_id, "proposal_creator"] = ctx.caller
    proposal_details[p_id, "description"] = description
    proposal_details[p_id, "time"] = now
    proposal_details[p_id, "type"] = "set_state"
    proposal_details[p_id, "duration"] = voting_time_in_days
    return p_id
@export 
def get_state(key: list): #Read state set by the set_state function. For future extensibility
    return misc[key]
@export
def get_active_contract(): #Get current AMM contract here
    return active_contract.get()
@export
def proposal_result(): #Get proposal result bool here
    for x in finished_proposals.get():
        if x == p_id:
            if status[p_id] != "":
                return status[p_id]
            return "undecided"
    return "proposal not found"
@export 
def proposal_information(p_id: int): #Get proposal information, provided as a dictionary
    info =	{
        "state": proposal_details[p_id, "state"],
        "key": proposal_details[p_id, "key"],
        "token_contract": proposal_details[p_id, "token_contract"],
        "contract": proposal_details[p_id, "contract"],
        "function": proposal_details[p_id, "function"],
        "kwargs": proposal_details[p_id, "kwargs"],
        "proposal_creator": proposal_details[p_id, "proposal_creator"],
        "description": proposal_details[p_id, "description"],
        "time": proposal_details[p_id, "time"],
        "type": proposal_details[p_id, "type"],
        "duration": proposal_details[p_id, "duration"],
        "reciever": proposal_details[p_id, "reciever"]
    }
    return info
@export 
def transfer(amount: float, to: str): #Basic token functionality starts here. This code is reasonably trustable
    assert amount > 0, 'Cannot send negative balances!'
    sender = ctx.caller
    assert balances[sender] >= amount, 'Not enough coins to send!'
    balances[sender] -= amount
    balances[to] += amount
@export
def balance_of(account: str):
    return balances[account]
@export
def allowance(owner: str, spender: str):
    return balances[owner, spender]
@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]
@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    sender = ctx.caller
    assert balances[main_account, sender] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, sender], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send!'
    balances[main_account, sender] -= amount
    balances[main_account] -= amount
    balances[to] += amount
@export 
def total_supply():
    return number_of_sig