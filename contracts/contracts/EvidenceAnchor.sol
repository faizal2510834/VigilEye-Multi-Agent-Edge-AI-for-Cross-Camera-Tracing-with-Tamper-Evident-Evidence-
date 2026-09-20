// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EvidenceAnchor {
    struct Evidence {
        bytes32 evidenceRoot;
        bytes32 caseId;
        uint256 timestamp;
        address submitter;
    }
    
    mapping(bytes32 => Evidence) public anchoredEvidence;
    
    event EvidenceAnchored(bytes32 indexed caseId, bytes32 indexed evidenceRoot, uint256 timestamp, address submitter);
    
    function anchor(bytes32 evidenceRoot, bytes32 caseId) public {
        require(anchoredEvidence[evidenceRoot].timestamp == 0, "Evidence already anchored");
        
        anchoredEvidence[evidenceRoot] = Evidence({
            evidenceRoot: evidenceRoot,
            caseId: caseId,
            timestamp: block.timestamp,
            submitter: msg.sender
        });
        
        emit EvidenceAnchored(caseId, evidenceRoot, block.timestamp, msg.sender);
    }
    
    function verify(bytes32 evidenceRoot) public view returns (bool exists, uint256 timestamp, address submitter) {
        Evidence memory ev = anchoredEvidence[evidenceRoot];
        if(ev.timestamp > 0) {
            return (true, ev.timestamp, ev.submitter);
        }
        return (false, 0, address(0));
    }
}
