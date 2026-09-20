import { expect } from "chai";
import { ethers } from "hardhat";

describe("EvidenceAnchor", function () {
  it("should anchor and verify evidence", async function () {
    const EvidenceAnchor = await ethers.getContractFactory("EvidenceAnchor");
    const anchor = await EvidenceAnchor.deploy();
    await anchor.waitForDeployment();

    const root = ethers.keccak256(ethers.toUtf8Bytes("merkle_root_test"));
    const caseId = ethers.keccak256(ethers.toUtf8Bytes("case_001"));

    await (await anchor.anchor(root, caseId)).wait();

    const result = await anchor.verify(root);
    expect(result.exists).to.equal(true);
    expect(result.timestamp).to.be.greaterThan(0n);
  });
});