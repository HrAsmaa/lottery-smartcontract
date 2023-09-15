from brownie import Lottery, accounts,config, network, exceptions;
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENV, fund_with_link, get_contract
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3;
import pytest

def test_getEntrenceFee():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  excepted_entrance_fee = Web3.toWei(1, "ether")
  entrence_fee = lottery.getEntrenceFee()
  assert entrence_fee == excepted_entrance_fee


def test_startLottery():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  lottery.startLottery({"from": account})
  assert lottery.lottery_state() == 0

def test_onlyOwner_startLottery():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  account2 = get_account(index=2)
  with pytest.raises(exceptions.VirtualMachineError):
    lottery.startLottery({"from": account2})
    request_id = tx.events["RequestRandomness"]["requestId"]



def test_can_enter_after_start():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  lottery.startLottery({"from": account})
  value = lottery.getEntrenceFee() +100000000
  lottery.enter({"from": account, "value": value})
  assert lottery.balance() == value

def test_cant_enter_before_start():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  value = lottery.getEntrenceFee() +100000000
  with pytest.raises(exceptions.VirtualMachineError):
    lottery.enter({"from": account, "value": value})

def test_can_endLottery_after_start():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  fund_with_link(lottery.address)
  lottery.startLottery({"from": account})
  value = lottery.getEntrenceFee() +100000000
  lottery.enter({"from": account, "value": value})
  lottery.endLottery({"from": account})
  assert lottery.lottery_state() == 2

def test_cant_endLottery_before_start():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  fund_with_link(lottery.address)
  tx = lottery.endLottery({"from": account})
  request_id = tx.events["RequestRandomness"]["requestId"]
  RANDOM_NUM = 777
  with pytest.raises(exceptions.VirtualMachineError):
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, RANDOM_NUM, lottery.address, {"from": account})

def test_pick_winner_correctly():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    pytest.skip()
  account = get_account()
  deploy_lottery()
  lottery = Lottery[-1]
  lottery.startLottery({"from": account})
  value = lottery.getEntrenceFee() +100000000
  lottery.enter({"from": account, "value": value})
  lottery.enter({"from": get_account(index=1), "value": value})
  lottery.enter({"from": get_account(index=2), "value": value})
  fund_with_link(lottery.address)
  account_balance = account.balance()
  lottery_balance = lottery.balance()
  tx = lottery.endLottery({"from": account})
  request_id = tx.events["RequestRandomness"]["requestId"]
  RANDOM_NUM = 777
  get_contract("vrf_coordinator").callBackWithRandomness(request_id, RANDOM_NUM, lottery.address, {"from": account})
  assert lottery.recentWinner() == account
  assert lottery.balance() == 0
  assert account.balance() == lottery_balance + account_balance
    