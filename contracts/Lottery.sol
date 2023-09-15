// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    uint256 usdEntrenceFee;
    AggregatorV3Interface ethUsdPriceFee;
    uint256 fee;
    bytes32 keyHash;
    address payable public recentWinner;
    uint256 randomNumber;
    event RequestRandomness(bytes32 requestId);
    enum LOTTERY_STATE {
        OPEN, //0
        CLOSED, //1
        CALCULATING_WINNER //2
    }
    LOTTERY_STATE public lottery_state;

    constructor(
        address _priceFeedAdress,
        address _vrfCordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(_vrfCordinator, _link) {
        usdEntrenceFee = 50 * (10 ** 18);
        ethUsdPriceFee = AggregatorV3Interface(_priceFeedAdress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        //Minimum 50$
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntrenceFee(), "Not Enough ETH");
        players.push(msg.sender);
    }

    function getEntrenceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFee.latestRoundData();
        uint256 priceUint = uint256(price) * (10 ** 10);
        uint256 minFee = (priceUint * (10 ** 18)) / priceUint;
        return minFee;
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't Start a new lottery"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
        RequestRandomness(requestId);
    }

    function fulfillRandomness(
        bytes32 requestId,
        uint256 randomness
    ) internal override {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "State Error"
        );
        require(randomness > 0, "random number equal 0");
        uint256 indexWinner = randomness % players.length;
        recentWinner = players[indexWinner];
        recentWinner.transfer(address(this).balance);
        // Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomNumber = randomness;
    }
}
