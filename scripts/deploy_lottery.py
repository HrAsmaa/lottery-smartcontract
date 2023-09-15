from brownie import Lottery, config, network;
from scripts.helpful_scripts import get_account, get_contract, fund_with_link;
import time

def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(get_contract("eth_usd_price_feed").address
                             ,get_contract("vrf_coordinator").address
                             ,get_contract("link_token").address
                             ,config["networks"][network.show_active()]["fee"]
                             ,config["networks"][network.show_active()]["key_hash"]
                             ,{"from": account}
                             ,publish_source = config["networks"][network.show_active()].get("verify", False)
                             )
    print("Deployed Lottery!")

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    transx = lottery.startLottery({"from": account})
    transx.wait(1) 
    print("The lottery is started!")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntrenceFee() + 100000000
    transx = lottery.enter({"from": account, "value": value})
    transx.wait(1)
    print("We entered the lottery!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    fund_tx = fund_with_link(lottery.address)
    fund_tx.wait(1)
    end_tx = lottery.endLottery({"from": account})
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the winner")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()