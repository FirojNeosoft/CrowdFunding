pragma solidity ^0.4.0;

contract CrowdFunder {
    
    address public creator;
    address public fundRecipient;
    uint public minimumToRaise;
    string campaignUrl; 
    // byte constant version = 0;

    // Data structures
    enum State {
        Fundraising,
        ExpiredRefund,
        Successful,
        Closed
    }

    struct Contribution {
        uint amount;
        address contributor;
    }
    // State variables
    State public state = State.Fundraising; // initialize on create
    uint public totalRaised;
    uint public currentBalance;
    uint public raiseBy;
    uint public completeAt;
    Contribution[] contributions;

    event LogFundingReceived(address addr, uint amount, uint currentTotal);
    event LogWinnerPaid(address winnerAddress);
    event LogFunderInitialized(
        address creator,
        address fundRecipient,
        string url,
        uint _minimumToRaise, 
        uint256 raiseby
    );

    modifier inState(State _state) {
        require(
            state != _state,
            "Invalid state."
        );
        _;
    }

    modifier isCreator() {
        require(
            msg.sender != creator,
            "Invalid state."
        );
        _;
    }

    // Wait 1 hour after final contract state before allowing contract destruction
    modifier atEndOfLifecycle() {
        require(
            !((state == State.ExpiredRefund || state == State.Successful) && completeAt + 1 hours < now),
            "Invalid state."
        );
        _;
    }

    constructor(
        uint timeInHoursForFundraising,
        string _campaignUrl,
        address _fundRecipient,
        uint _minimumToRaise) public
    {
        creator = msg.sender;
        fundRecipient = _fundRecipient;
        campaignUrl = _campaignUrl;
        minimumToRaise = _minimumToRaise; //convert to wei
        raiseBy = now + (timeInHoursForFundraising * 1 hours);
        currentBalance = 0;
        state = State.Fundraising; // initialize on create
        emit LogFunderInitialized(
            creator,
            fundRecipient,
            campaignUrl,
            minimumToRaise,
            raiseBy);
    }

    function contribute(address sender, uint value) public payable returns (uint256)
    {
        contributions.push(
            Contribution({
                amount: value,
                contributor: sender
                }) // use array, so can iterate
            );
        totalRaised += value;
        currentBalance = totalRaised;
        emit LogFundingReceived(sender, value, totalRaised);

        checkIfFundingCompleteOrExpired();
        return contributions.length - 1; // return id
    }
    
    function getCreator() view public returns (address) {
        return creator;
    }
    
    function getExpiry() view public returns (uint) {
        return raiseBy;
    }

    function getTarget() view public returns (uint) {
        return minimumToRaise;
    }

    function getReceiver() view public returns (address) {
        return fundRecipient;
    }
    
    function getBalance() view public returns (uint) {
        return currentBalance;
    }
    
    function getState() view public returns (string) {
       if (state == State.Fundraising) {
           return "Fundraising";
       } else if (state == State.ExpiredRefund){
           return "ExpiredRefund";
       } else if (state == State.Successful){
           return "Successful";
       } else {
           return "Closed";
       }
    }

    function checkIfFundingCompleteOrExpired() public {
        if (totalRaised > minimumToRaise) {
            state = State.Successful;
            payOut();

            // could incentivize sender who initiated state change here
            } else if ( now > raiseBy )  {
                state = State.ExpiredRefund; // backers can now collect refunds by calling getRefund(id)
            }
            completeAt = now;
        }

        function payOut() public inState(State.Successful)
        {
            // if(!fundRecipient.send(this.balance)) {
            //     throw;
            // }
            state = State.Closed;
            currentBalance = 0;
            emit LogWinnerPaid(fundRecipient);
        }

        function getRefund(address u) public inState(State.ExpiredRefund) returns (bool)
        {
            // if (contributions.length <= id || id < 0 || contributions[id].amount == 0 ) {
            //     throw;
            // }
            uint index;
            for (uint i = 0; i < contributions.length; i++) {
                if (contributions[i].contributor == u) {
                    index=i;
                }
             }

            uint amountToRefund = contributions[index].amount;
            contributions[index].amount = 0;

            // if(!u.send(amountToRefund)) {
            //     contributions[index].amount = amountToRefund;
            //     return false;
            // }
            // else{
                totalRaised -= amountToRefund;
                currentBalance = totalRaised;
            // }

            return true;

        }

        function removeContract() public isCreator() atEndOfLifecycle()
        {
            selfdestruct(msg.sender);
            // creator gets all money that hasn't be claimed
        }
    }
