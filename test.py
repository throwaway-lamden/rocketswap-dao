import unittest
from contracting.client import ContractingClient
client = ContractingClient()

class standardTests(unittest.TestCase):
    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()
        with open('currency.py') as f:
            code = f.read()
            client.submit(code, name='currency')
        with open('sc.py') as f:
            code = f.read()
            client.submit(code, name='sc')
        self.sc = client.get_contract("sc")
        self.currency = client.get_contract("currency")
        self.sc.transfer(amount=4750000, to="wallet2", signer="wallet1")
        self.sc.transfer(amount=500000, to="wallet3", signer="wallet1")
        
    def tearDown(self):
        self.client.flush()
        
    def test_create_proposal_works(self):
        self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=1)
        
    def test_create_proposal_returns_correct_value(self):
        p_id = self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=1)
        assert p_id == 0
        
    def test_create_proposal_updates_next_pid(self):
        self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=1)
        p_id = self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=1)
        assert p_id == 1
        
    def test_create_proposal_sets_correct_default_state(self):
        p_id = self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=1)
        
        assert proposal_details[p_id, "resolved"] == False
        assert proposal_details[p_id, "proposal_creator"] == 'sys' # double check default value is sys
        assert proposal_details[p_id, "time"] == now
        
     def test_create_proposal_sets_correct_user_state(self):
        p_id = self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=1)
        
        assert proposal_details[p_id, "type"] == 'banjos'
        assert proposal_details[p_id, "args"] == ['test', 'test']
        assert proposal_details[p_id, "description"] == 'stu'
        assert proposal_details[p_id, "duration"] == 1
        
    def test_create_proposal_under_minimum_time_assert_fail(self):
        with self.assertRaises(AssertionError):
            self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=0)
        
    def test_vote_works(self):
        p_id = self.sc.create_proposal(proposal_type='banjos', proposal_args=['test', 'test'], description='stu', voting_time_in_days=1)
        self.sc.vote(p_id=p_id, amount=500, decision=True, signer='wallet1')
        
    def test_vote_sets_state(self):
        
    def test_vote_not_bool_assert_fail(self):
        
    def test_vote_twice_assert_fail(self):
        
    def test_vote_for_nonexistent_pid_assert_fail(self):
        
    
if __name__ == '__main__':
    unittest.main()
