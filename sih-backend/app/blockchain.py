"""
Blockchain Client for BlueCarbon (Celo Alfajores) with Contract Registry
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv
from typing import Dict, Any

# Load env variables
load_dotenv()


class BlueCarbonClient:
    def __init__(self):
        # Connect to Celo Alfajores
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
        if not self.w3.is_connected():
            raise ConnectionError("❌ Failed to connect to Celo Alfajores")

        print(f"✅ Connected to Celo Alfajores - Block: {self.w3.eth.block_number}")

        # --- Load Registry Contract ---
        registry_address = Web3.to_checksum_address(os.getenv("REGISTRY_ADDRESS"))
        registry_abi_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "abi", "ContractRegistry.json"
        )

        with open(registry_abi_path, "r") as f:
            registry_abi = json.load(f)

        self.registry = self.w3.eth.contract(address=registry_address, abi=registry_abi)
        print(f"📒 Registry loaded at {registry_address}")

        # --- Fetch BlueCarbon contract address from registry ---
        bluecarbon_address = self.registry.functions.getContract("BlueCarbon").call()
        if bluecarbon_address == "0x0000000000000000000000000000000000000000":
            raise ValueError("❌ No BlueCarbon contract registered in ContractRegistry")

        print(f"📌 BlueCarbon address from registry: {bluecarbon_address}")

        # --- Load BlueCarbon contract ABI ---
        bluecarbon_abi_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "abi", "BlueCarbon.json"
        )

        with open(bluecarbon_abi_path, "r") as f:
            bluecarbon_abi = json.load(f)

        self.contract = self.w3.eth.contract(address=bluecarbon_address, abi=bluecarbon_abi)
        self.contract_address = bluecarbon_address

        print(f"📄 BlueCarbon contract loaded at {self.contract_address}")

    # --------- READ METHODS --------- #
    def get_project_token_id(self, project_id: str) -> int:
        """Fetch token ID for a project by its projectId"""
        return self.contract.functions.getProjectTokenId(project_id).call()

    def get_balance_of(self, account: str, token_id: int) -> int:
        """Check ERC1155 balance of a user for a given tokenId"""
        return self.contract.functions.balanceOf(
            Web3.to_checksum_address(account), token_id
        ).call()

    def get_token_metadata(self, token_id: int) -> str:
        """Fetch IPFS CID metadata of a token"""
        return self.contract.functions.getTokenMetadataCID(token_id).call()

    def get_token_proof(self, token_id: int) -> str:
        """Fetch proof CID for issued credits"""
        return self.contract.functions.getTokenProofCID(token_id).call()

    # --------- WRITE METHODS --------- #
    def _send_transaction(self, txn, private_key: str) -> Dict[str, Any]:
        """Helper to sign, send, and wait for confirmation"""
        acct = self.w3.eth.account.from_key(private_key)
        signed = self.w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            "tx_hash": tx_hash.hex(),
            "status": receipt.status,
            "blockNumber": receipt.blockNumber,
        }

    def register_project(
        self, project_id: str, metadata_cid: str, private_key: str
    ) -> Dict[str, Any]:
        """Register a new project on-chain (admin only)"""
        acct = self.w3.eth.account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(acct.address)

        txn = self.contract.functions.registerProject(
            project_id, metadata_cid
        ).build_transaction(
            {
                "from": acct.address,
                "nonce": nonce,
                "chainId": int(os.getenv("CHAIN_ID")),
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        result = self._send_transaction(txn, private_key)
        print(f"📝 Project registered: {project_id} → Tx: {result['tx_hash']}")
        return result

    def issue_credits(
        self, to_address: str, project_id: str, amount: int, proof_cid: str, private_key: str
    ) -> Dict[str, Any]:
        """Issue carbon credits (minter only)"""
        acct = self.w3.eth.account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(acct.address)

        txn = self.contract.functions.issueCredits(
            Web3.to_checksum_address(to_address), project_id, amount, proof_cid
        ).build_transaction(
            {
                "from": acct.address,
                "nonce": nonce,
                "chainId": int(os.getenv("CHAIN_ID")),
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        result = self._send_transaction(txn, private_key)
        print(f"💰 Issued {amount} credits for project {project_id} → Tx: {result['tx_hash']}")
        return result

    def retire_credits(self, token_id: int, amount: int, private_key: str) -> Dict[str, Any]:
        """Retire carbon credits (user)"""
        acct = self.w3.eth.account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(acct.address)

        txn = self.contract.functions.retireCredits(token_id, amount).build_transaction(
            {
                "from": acct.address,
                "nonce": nonce,
                "chainId": int(os.getenv("CHAIN_ID")),
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        result = self._send_transaction(txn, private_key)
        print(f"🔥 Retired {amount} credits (Token {token_id}) → Tx: {result['tx_hash']}")
        return result


# Global instance
bluecarbon_client = BlueCarbonClient()
