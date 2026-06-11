"""Token approval checker — detect risky allowances."""
import requests

# Known risky/spam spender addresses
KNOWN_RISKY = {
    '0x0000000000000000000000000000000000000000': 'zero_address',
}

MAX_SAFE_ALLOWANCE = 10**30  # ~1 billion tokens

class ApprovalChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'ApprovalChecker/1.0'
    
    def get_approvals(self, wallet, chain='ethereum'):
        try:
            rpc = self._get_rpc(chain)
            # Get approval events (Transfer topic0 for Approval event)
            approval_topic = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'
            
            # Use eth_getLogs to find Approval events
            payload = {
                "jsonrpc": "2.0", "id": 1,
                "method": "eth_getLogs",
                "params": [{
                    "topics": [approval_topic, self._pad_address(wallet)],
                    "fromBlock": "0x" + format(self._get_recent_block(rpc) - 10000, 'x'),
                    "toBlock": "latest"
                }]
            }
            resp = self.session.post(rpc, json=payload, timeout=15)
            logs = resp.json().get('result', [])
            
            approvals = []
            seen = set()
            for log in logs:
                token_addr = log.get('address', '')
                spender = '0x' + log.get('topics', [''])[2][-40:] if len(log.get('topics', [])) > 2 else ''
                key = f"{token_addr}:{spender}"
                
                if key in seen:
                    continue
                seen.add(key)
                
                allowance = int(log.get('data', '0x0'), 16)
                risk = self._assess_risk(allowance, spender)
                
                approvals.append({
                    'token': token_addr,
                    'spender': spender,
                    'allowance': 'unlimited' if allowance > MAX_SAFE_ALLOWANCE else str(allowance),
                    'risk': risk
                })
            
            return approvals
        except:
            return []
    
    def _assess_risk(self, allowance, spender):
        if spender.lower() in KNOWN_RISKY:
            return 'critical'
        if allowance > MAX_SAFE_ALLOWANCE:
            return 'high'
        if allowance > MAX_SAFE_ALLOWANCE // 100:
            return 'medium'
        return 'low'
    
    def _get_rpc(self, chain):
        rpcs = {
            'ethereum': 'https://eth.llamarpc.com',
            'base': 'https://mainnet.base.org',
            'arbitrum': 'https://arb1.arbitrum.io/rpc',
        }
        return rpcs.get(chain, rpcs['ethereum'])
    
    def _get_recent_block(self, rpc):
        try:
            payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}
            resp = self.session.post(rpc, json=payload, timeout=10)
            return int(resp.json().get('result', '0x0'), 16)
        except:
            return 20000000
    
    def _pad_address(self, addr):
        return '0x' + addr[2:].lower().zfill(64)
