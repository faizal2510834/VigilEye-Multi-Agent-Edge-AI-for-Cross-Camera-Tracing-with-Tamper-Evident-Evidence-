import { ethers } from "hardhat";
import * as fs from "fs";

async function main() {
  const EvidenceAnchor = await ethers.getContractFactory("EvidenceAnchor");
  const anchor = await EvidenceAnchor.deploy();
  await anchor.waitForDeployment();
  const address = await anchor.getAddress();
  console.log(`EvidenceAnchor deployed to ${address}`);
  fs.writeFileSync("deployed_address.txt", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});