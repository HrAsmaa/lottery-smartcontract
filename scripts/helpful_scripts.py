from brownie import network, accounts, config, MockV3Aggregator, Contract, LinkToken, VRFCoordinatorMock

DECIMALS = 8
STARTING_PRICE = 200000000000
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORK_BLOCKCHAIN_ENV = ["mainnet-fork-dev"]
contract_to_mock ={ 
    "eth_usd_price_feed": MockV3Aggregator,
    "link_token": LinkToken,
    "vrf_coordinator": VRFCoordinatorMock,
 }


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORK_BLOCKCHAIN_ENV:
        return accounts [0]
    return accounts.add(config["wallets"]["from_key"])

def get_contract(name):
    """
    This method will grab the contract adress if deployed , otherwise it will deploy a mock 
    and return it.
        Args:
          name : The contract name
        Returns:
          most recent version of contract deployed
    """
    contract_type = contract_to_mock[name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type)<=0:
            deploy_mocks()
        return contract_type[-1]
    else:
        contract_adress = config["networks"][network.show_active()][name]
        contract = Contract.from_abi(contract_type.name,contract_adress,contract_type.abi)
        return contract
        

def deploy_mocks():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

def fund_with_link(contract_address, _account=None, _link_token=None, amount=250000000000000000):
    account = _account if _account else get_account()
    link_token = _link_token if _link_token else get_contract("link_token")
    # create a contract using her adress and an interface
    #link_token = interface.LinkTokenInterface(link_token.adress)
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx