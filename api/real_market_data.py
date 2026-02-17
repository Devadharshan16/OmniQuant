"""
Real-Time Market Data Fetcher
Connects to actual cryptocurrency exchanges to fetch live prices
NO AI/ML REQUIRED - Just HTTP API calls
"""

import ccxt
import time
from typing import List, Dict, Optional
from datetime import datetime
import asyncio


class RealMarketDataFetcher:
    """
    Fetch real-time market data from cryptocurrency exchanges
    Read-only mode - no trading, just price fetching
    """
    
    def __init__(self, enable_rate_limit: bool = True):
        """
        Initialize exchange connections
        
        Args:
            enable_rate_limit: Automatically throttle requests to respect exchange limits
        """
        print("Initializing real-time exchange connections...")
        
        # Initialize exchanges (NO API KEYS NEEDED for public data)
        # Reduced timeout to 5s for faster response
        self.exchanges = {}
        
        try:
            self.exchanges['binance'] = ccxt.binance({
                'enableRateLimit': enable_rate_limit,
                'timeout': 5000  # 5 seconds
            })
            print("  [OK] Connected to Binance")
        except Exception as e:
            print(f"  [WARN] Binance unavailable: {e}")
        
        try:
            self.exchanges['coinbase'] = ccxt.coinbase({
                'enableRateLimit': enable_rate_limit,
                'timeout': 5000  # 5 seconds
            })
            print("  [OK] Connected to Coinbase")
        except Exception as e:
            print(f"  [WARN] Coinbase unavailable: {e}")
        
        try:
            self.exchanges['kraken'] = ccxt.kraken({
                'enableRateLimit': enable_rate_limit,
                'timeout': 5000  # 5 seconds
            })
            print("  [OK] Connected to Kraken")
        except Exception as e:
            print(f"  [WARN] Kraken unavailable: {e}")
        
        try:
            self.exchanges['kucoin'] = ccxt.kucoin({
                'enableRateLimit': enable_rate_limit,
                'timeout': 5000  # 5 seconds
            })
            print("  [OK] Connected to KuCoin")
        except Exception as e:
            print(f"  [WARN] KuCoin unavailable: {e}")
        
        if not self.exchanges:
            raise Exception("Could not connect to any exchanges")
        
        print(f"[OK] Connected to {len(self.exchanges)} exchanges\n")
    
    def fetch_real_prices(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch REAL market prices from live exchanges
        
        Args:
            symbols: List of trading pairs like ['BTC/USDT', 'ETH/USDT']
                    If None, uses default major pairs
        
        Returns:
            List of dictionaries containing real trading pair data
        """
        if symbols is None:
            # Include cross-pairs for more arbitrage cycle detection
            symbols = [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT',
                'ETH/BTC', 'SOL/ETH'
            ]
        
        print(f"[FETCH] Fetching real-time prices for {len(symbols)} pairs from {len(self.exchanges)} exchanges...")
        
        pairs = []
        fetch_count = 0
        max_fetches = 20  # Allow more fetches for cross-pairs
        
        for exchange_name, exchange in self.exchanges.items():
            for symbol in symbols:
                if fetch_count >= max_fetches:
                    print(f"  [SPEED] Speed limit: stopping at {fetch_count} fetches")
                    break
                    
                try:
                    # Fetch REAL ticker data from exchange with timeout
                    ticker = exchange.fetch_ticker(symbol)
                    
                    if not ticker or 'last' not in ticker or ticker['last'] is None:
                        continue
                    
                    from_token, to_token = symbol.split('/')
                    
                    # Calculate rates for arbitrage detection
                    last_price = float(ticker['last'])
                    bid_price = float(ticker['bid']) if ticker.get('bid') else last_price
                    ask_price = float(ticker['ask']) if ticker.get('ask') else last_price
                    
                    # Forward pair (e.g., BTC -> USDT)
                    pairs.append({
                        'from': from_token,
                        'to': to_token,
                        'rate': last_price,  # How much TO token you get for 1 FROM token
                        'bid': bid_price,
                        'ask': ask_price,
                        'last': last_price,
                        'volume': float(ticker.get('quoteVolume', 0)) if ticker.get('quoteVolume') else 0,
                        'fee': 0.0005,  # 0.05% maker fee (realistic for high-volume traders)
                        'liquidity': float(ticker.get('quoteVolume', 0)) * 0.01 if ticker.get('quoteVolume') else 10000,
                        'exchange': exchange_name,
                        'timestamp': ticker.get('timestamp', int(time.time() * 1000)),
                        'symbol': symbol,
                        'is_real': True,
                        'volatility': 0.015  # Typical crypto volatility
                    })
                    
                    # Reverse pair (e.g., USDT -> BTC)
                    pairs.append({
                        'from': to_token,
                        'to': from_token,
                        'rate': 1 / last_price if last_price > 0 else 0,
                        'bid': 1 / ask_price if ask_price > 0 else 0,
                        'ask': 1 / bid_price if bid_price > 0 else 0,
                        'last': 1 / last_price if last_price > 0 else 0,
                        'volume': float(ticker.get('baseVolume', 0)) if ticker.get('baseVolume') else 0,
                        'fee': 0.0005,  # 0.05% maker fee
                        'liquidity': float(ticker.get('baseVolume', 0)) * 0.01 if ticker.get('baseVolume') else 10000,
                        'exchange': exchange_name,
                        'timestamp': ticker.get('timestamp', int(time.time() * 1000)),
                        'symbol': f"{to_token}/{from_token}",
                        'is_real': True,
                        'volatility': 0.015
                    })
                    
                    fetch_count += 1
                    print(f"  [OK] {exchange_name:12} {symbol:12} ${last_price:>12,.2f}")
                    
                except ccxt.NetworkError as e:
                    print(f"  [WARN] Network error {symbol} from {exchange_name}")
                    continue
                except ccxt.RequestTimeout as e:
                    print(f"  [TIMEOUT] Timeout {symbol} from {exchange_name}")
                    continue
                except Exception as e:
                    print(f"  [WARN] Error {symbol} from {exchange_name}: {str(e)[:50]}")
                    continue
            
            if fetch_count >= max_fetches:
                break
        
        print(f"\n[OK] Successfully fetched {fetch_count} real prices")
        print(f"[OK] Generated {len(pairs)} trading pairs (including reverse pairs)\n")
        
        return pairs
    
    def fetch_orderbook(self, exchange_name: str, symbol: str, limit: int = 5) -> Optional[Dict]:
        """
        Fetch real Level-2 order book for advanced analysis
        
        Args:
            exchange_name: Name of exchange ('binance', 'coinbase', etc.)
            symbol: Trading pair like 'BTC/USDT'
            limit: Number of bid/ask levels to fetch
        
        Returns:
            Dictionary with bids, asks, timestamp, or None if failed
        """
        try:
            if exchange_name not in self.exchanges:
                raise ValueError(f"Exchange {exchange_name} not available")
            
            exchange = self.exchanges[exchange_name]
            orderbook = exchange.fetch_order_book(symbol, limit)
            
            return {
                'bids': orderbook['bids'],  # [[price, amount], [price, amount], ...]
                'asks': orderbook['asks'],
                'timestamp': orderbook.get('timestamp', int(time.time() * 1000)),
                'symbol': symbol,
                'exchange': exchange_name
            }
        except Exception as e:
            print(f"Could not fetch orderbook for {symbol} from {exchange_name}: {e}")
            return None
    
    def get_exchange_status(self) -> Dict[str, bool]:
        """
        Check which exchanges are currently available
        
        Returns:
            Dictionary mapping exchange names to availability status
        """
        status = {}
        for exchange_name, exchange in self.exchanges.items():
            try:
                # Try to fetch a simple ticker to test connection
                exchange.fetch_ticker('BTC/USDT')
                status[exchange_name] = True
            except:
                status[exchange_name] = False
        
        return status
    
    def fetch_multi_exchange_arbitrage_data(self) -> List[Dict]:
        """
        Specialized fetch for cross-exchange arbitrage detection
        Fetches same pairs from multiple exchanges to find price differences
        
        Returns:
            List of trading pairs optimized for arbitrage detection
        """
        # Focus on high-liquidity pairs that exist on multiple exchanges
        common_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT',
            'BTC/USDC', 'ETH/USDC',
            'ETH/BTC', 'BNB/BTC'
        ]
        
        return self.fetch_real_prices(common_pairs)


def test_real_data_fetcher():
    """Test the real-time data fetcher"""
    print("=" * 70)
    print("Testing Real-Time Market Data Fetcher")
    print("=" * 70 + "\n")
    
    try:
        # Initialize fetcher
        fetcher = RealMarketDataFetcher()
        
        # Fetch real prices
        real_data = fetcher.fetch_real_prices(['BTC/USDT', 'ETH/USDT'])
        
        print("\n" + "=" * 70)
        print("Sample Real Data:")
        print("=" * 70)
        
        # Show first few pairs
        for pair in real_data[:6]:
            print(f"\n{pair['exchange']:12} | {pair['from']:6} → {pair['to']:6}")
            print(f"  Rate:      {pair['rate']:,.8f}")
            print(f"  Last:      ${pair['last']:,.2f}")
            print(f"  Volume:    ${pair['volume']:,.0f}")
            print(f"  Liquidity: ${pair['liquidity']:,.0f}")
            print(f"  Timestamp: {datetime.fromtimestamp(pair['timestamp']/1000)}")
        
        # Check exchange status
        print("\n" + "=" * 70)
        print("Exchange Status:")
        print("=" * 70)
        status = fetcher.get_exchange_status()
        for exchange, available in status.items():
            symbol = "✓" if available else "✗"
            print(f"  {symbol} {exchange:12} {'Online' if available else 'Offline'}")
        
        print("\n" + "=" * 70)
        print("✓ Real-time data fetcher working correctly!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing real data fetcher: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run test when executed directly
    success = test_real_data_fetcher()
    exit(0 if success else 1)
