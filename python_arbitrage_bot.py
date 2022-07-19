"""
    uniswap v2 exchange formula
    x * y = k
    After a transaction the value of token x will increase by a, the amount you sell, and token y will decrease by b, the amount you purchase
    (x + a) * (y - b) = k
    xy - xb + ay - ab = k
    k - xb + ay - ab = k
    ay - xb - ab = 0
    ay = xb + ab
    ay/(x + a) = b
    
    For the second exchange we use the input of b, the output from the rpevious exchange, and change the other variables to show they are distinct from the first dex
    n * m = q
    (n + b) * (m - c) = q
    bn - mc - bc = 0
    bn = mc + bc
    bn/(m + b) = c
    
    Plug in the output from our first dex
    c = (ay/(x + a))m/(n + (ay/(x + a)))
    
    We now have a function for calculating the amount of the same coin we will receive after selling it on one dex then immediately buying them back on another based upon the amount we initially put in, a
    
    We see that we want to maximize this function, the difference between our output and input amounts
    (ay/(x + a))m/(n + (ay/(x + a))) - a
    
    Or alternatively we can minimize its additive inverse
    a - (ay/(x + a))m/(n + (ay/(x + a)))
    
    We must also account for fees of 0.3% on each trade, which we make two of
    a - (1-0.003)((1-0.003)ay/(x + (1-0.003)a))m/(n + (1-0.003)((1-0.003)ay/(x + (1-0.003)a))) = a - (0.997)((0.997)ay/(x + (0.997)a))m/(n + (0.997)((0.997)ay/(x + (0.997)a)))
    
    We are now ready to determine whenever a valid, profitable, arbitrage opportunity is available when we can find a negative value for the function
    a - (0.997)((0.997)ay/(x + (0.997)a))m/(n + (0.997)((0.997)ay/(x + (0.997)a)))
    
    we see that we cant sell a negative amount of coins, x>=0, and whenever x is zero that the output will also be zero. So, if this function is greater than or equal to zero whenever a > 0 
    then we will have a result of a = 0 from our optimization process and the conclusion will be that there is no opportunity for arbitrage.
    
    In the code below we substitute a with x
    
    This process should be expanded to account for gas fees as well
    
"""

from web3 import Web3
w3 = Web3(Web3.HTTPProvider("https://cloudflare-eth.com"))

token_addr1 = "0x6B175474E89094C44Da98b954EedeAC495271d0F"    # DAI 
token_addr2 = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"    # WETH

acc_address = "0x67DdEbd4D6c39569e44FD7491B64079Fc1fe15E3"    # Uniswap V2: DAI 2

#uniswap v2 router addresses
uniswap_routers = ["0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D","0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F","0x03f7724180AA6b939894B5Ca4314783B0b36b329","0x9C578b573EdE001b95d51a55A3FAfb45f5608b1f","0xCeB90E4C17d626BE0fACd78b79c9c87d7ca181b3"]

#uniswap liquidity pools
uniswap_lps = ["0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11","0xC3D03e4F041Fd4cD388c549Ee2A29a9E5075882f","0x8faf958E36c6970497386118030e6297fFf8d275","0x2ad95483ac838E2884563aD278e933fba96Bc242","0x60A26d69263eF43e9a68964bA141263F19D71D51"]         

# This is a simplified Contract Application Binary Interface (ABI) of an ERC-20 Token Contract.
erc20_abi = [
    {
        'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    }
]



uniswap_router_abi = [
    {
        "inputs":[],
        "name":"WETH",
        "outputs":[{"internalType":"address","name":"","type":"address"}],
        "stateMutability":"view","type":"function"
    }, 
    {
        "inputs":[],
        "name":"factory",
        "outputs":[{"internalType":"address","name":"","type":"address"}],
        "stateMutability":"view","type":"function"
    }, 
    {
        "inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],
        "name": "getAmountsIn",
        "outputs": [{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],
        "stateMutability":"view","type":"function"
    },
    {
        "inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],
        "name": "getAmountsOut",
        "outputs": [{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],
        "stateMutability":"view","type":"function"
    },
    {
        "inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],
        "name":"getAmountOut",
        "outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],
        "stateMutability":"pure","type":"function"
    }
]


uniswap_factory_abi = [
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "allPairs",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view", "type": "function", "constant": True
    },
    {
        "inputs": [],
        "name": "allPairsLength",
        "outputs": [{"internalType":"uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view", "type": "function", "constant": True
    }
]

uniswap_liquiidty_pool_abi = [
    {
        "constant":True,
        "inputs":[],
        "name":"token0",
        "outputs":[{"internalType":"address", "name":"", "type":"address"}],
        "payable":False, "stateMutability":"view", "type":"function"
    },
    {
        "constant":True,
        "inputs":[],
        "name":"token1",
        "outputs":[{"internalType":"address", "name":"", "type":"address"}],
        "payable":False, "stateMutability":"view", "type":"function"
    }
]


exchange = []
exchangeRate = []
balances = []
path = [token_addr1, token_addr2]
reverse_path = [token_addr2, token_addr1]

#get erc20 token balances for each liquidity pool and both tokens on all 5 exchanges
for i in range(0, len(uniswap_lps)):
  contract1 = w3.eth.contract(address=w3.toChecksumAddress(token_addr1), abi=erc20_abi)
  contract2 = w3.eth.contract(address=w3.toChecksumAddress(token_addr2), abi=erc20_abi)
  balances += [[contract1.functions.balanceOf(uniswap_lps[i]).call(), contract2.functions.balanceOf(uniswap_lps[i]).call()]]
  exchange += [w3.eth.contract(address=w3.toChecksumAddress(uniswap_routers[i]), abi=uniswap_router_abi)]

print("Liquidity Pool Balances of DAI and WETH respectively ", balances)
from mystic import reduced
from mystic.solvers import diffev2
from mystic.monitors import VerboseMonitor
from numpy.random import rand

for i in range(0, (len(balances) - 1)):
  for h in range(0, len(balances)):
    if h == i:
      continue
    #define function for amount of coins returned after selling x coins on one exchange and buying them back on another
    def objective(x): 
      return (x[0] - (0.997) * ((0.997) * x[0] * balances[i][1]/(balances[i][0] + (0.997) * x[0])) * balances[h][0]/(balances[h][1] + (0.997) * ((0.997) * x[0] * balances[i][1]/(balances[i][0] + (0.997) * x[0]))))
    # define range for input
    r_min = 0
    r_max = 10**22
    bounds = [(r_min, r_max)]
    mon = VerboseMonitor(10)
    
    # define the starting point as a random sample from the domain
    pt = int(r_min + rand(1) * (r_max - r_min))
    print("Random Starting Value: ", pt, " ")
    #Optimize function for calculating coins returned from arbitraging exchanges
    try:
      result = diffev2(objective, x0=[pt], bounds=bounds, npop=40, ftol=1e-8, disp=False, full_output=True, itermon=mon)
    except Exception as e:
      print("Error: ", e)
    # summarize the result
    print("LP Addresses", uniswap_lps[i], ",  ", uniswap_lps[h])
    print("Calculated Optimal amount DAI bought: ", result[0][0], " amount received back", result[1])
    solution = int(result[0][0])
    # If suggested amount of stable-coins to use for purchase is less than 1,000,000/10^6 then don't perform arbitrage
    # Tolerance will likely need to be adjusted for arbitrage to be profitable and correct for coins with different amounts of decimal places
    if solution > 10**6:
      real_value = exchange[h].functions.getAmountsOut(exchange[i].functions.getAmountsOut(int(solution * 0.99), path).call()[1], reverse_path).call()[1]
      print("Amount Bought: ", int(solution * 0.99), "Amount received: ", real_value, ", Profit: ", real_value - int(solution * 0.99))
      real_value = exchange[h].functions.getAmountsOut(exchange[i].functions.getAmountsOut(int(solution), path).call()[1], reverse_path).call()[1]
      print("Amount Bought: ", int(solution), "Amount received: ", real_value, ", Profit: ", real_value - int(solution))
      real_value = exchange[h].functions.getAmountsOut(exchange[i].functions.getAmountsOut(int(solution * 1.01), path).call()[1], reverse_path).call()[1]
      print("Amount Bought: ", int(solution * 1.01), "Amount received: ", real_value, ", Profit: ", real_value - int(solution * 1.01))
    else:
      print("<br> 0 - no arbitrage performed")
    #newline to seperate outputs
    print()
    
    
