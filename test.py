import unittest
from contracting.client import ContractingClient
client = ContractingClient()

with open('currency.py') as f:
    code = f.read()
    client.submit(code, name='currency')
currency = client.get_contract("currency")

with open('sc.py') as f:
    code = f.read()
    client.submit(code, name='sc')


class MyTestCase(unittest.TestCase):
    def setUp():
        self.client = ContractingClient()
        self.client.flush()
        sc = client.get_contract("sc")
        currency = client.get_contract("currency")
        sc.transfer(amount=4750000, to="wallet2", signer="wallet1")
        sc.transfer(amount=500000, to="wallet3", signer="wallet1")
    def tearDown():
        self.client.flush()
    self.client.flush()
    def test_CAP_pass(self):
        sc.change_minimum_percentage(new_percentage=0.6, description="test transfer", voting_time_in_days=0, signer='wallet1') #perform one, or multiple actions
        sc.vote(p_id="0", result=True, signer='wallet1')
        sc.vote(p_id="0", result=True, signer='wallet2')
        sc.vote(p_id="0", result=False, signer='wallet3')
        self.assertEqual(sc.determine_results(p_id=0), True)
        self.assertEqual(sc.quick_read('required_approval_percentage'), 0.6)
        sc.change_minimum_percentage(new_percentage=0.3, description="test transfer", voting_time_in_days=0, signer='wallet1') #perform one, or multiple actions
        sc.vote(p_id="1", result=True, signer='wallet1')
        sc.vote(p_id="1", result=True, signer='wallet2')
        sc.vote(p_id="1", result=False, signer='wallet3')
        self.assertEqual(sc.determine_results(p_id=0), True)
        self.assertEqual(sc.quick_read('required_approval_percentage'), 0.3)
    def test_CMD_pass(self):
        sc.change_minimum_duration(new_minimum_amount=300, description="test transfer", voting_time_in_days=0, signer='wallet1') #perform one, or multiple actions
        sc.vote(p_id="0", result=True, signer='wallet1')
        sc.vote(p_id="0", result=True, signer='wallet2')
        sc.vote(p_id="0", result=False, signer='wallet3')
        self.assertEqual(sc.determine_results(p_id=0), True)
        self.assertEqual(sc.quick_read('minimum_proposal_duration'), 300)
    def test_CTP_pass_and_proposal_return(self):
        sc.create_transfer_proposal(token_contract="currency", amount=100, to="wallet4", description="test transfer", voting_time_in_days=0, signer='wallet1') #perform one, or multiple actions
        return_dict = sc.proposal_information(p_id=0, signer='wallet1')
        self.assertEqual(return_dict["token_contract"], 0) 
        sc.vote(p_id="0", result=True, signer='wallet1')
        sc.vote(p_id="0", result=True, signer='wallet2')
        sc.vote(p_id="0", result=False, signer='wallet3')
        self.assertEqual(sc.determine_results(p_id=0), True)
        self.assertEqual(currency.balance_of(account="wallet4"), 100)
    def test_CSV_pass(self):
        sc.create_signalling_vote(action="do a test", description="test transfer", voting_time_in_days=0, signer='wallet1') #perform one, or multiple actions
        sc.vote(p_id="0", result=True, signer='wallet1')
        sc.vote(p_id="0", result=True, signer='wallet2')
        sc.vote(p_id="0", result=False, signer='wallet3')
        self.assertEqual(sc.determine_results(p_id=0), True)
        return_dict = sc.proposal_information(p_id=0, signer='wallet1')
        self.assertEqual(return_dict["token_contract"], "do a test") 
    def test_CTP_fail(self):
        sc.create_transfer_proposal(token_contract="currency", amount=100, to="wallet4", description="test transfer", voting_time_in_days=0, signer='wallet1')
        print(sc.proposal_information(p_id=0, signer='wallet1'))
        sc.vote(p_id="0", result=True, signer='wallet1')
        sc.vote(p_id="0", result=False, signer='wallet2')
        sc.vote(p_id="0", result=False, signer='wallet3')
        self.assertEqual(sc.determine_results(p_id=0), False)
        self.assertEqual(currency.balance_of(account="wallet4"), 0)
if __name__ == '__main__':
    unittest.main()