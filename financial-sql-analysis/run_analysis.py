"""
Financial Data Analysis - SQL Case Study
Author: Mohamed Lamkadmi

This script creates a SQLite database with sample financial data
and runs all analysis queries. No external database needed.
"""

import sqlite3
import pandas as pd

# Create in-memory database
conn = sqlite3.connect(':memory:')
cur = conn.cursor()

# Create tables
cur.executescript('''
CREATE TABLE securities (
    id INTEGER PRIMARY KEY,
    ticker TEXT,
    name TEXT,
    sector TEXT,
    asset_class TEXT,
    duration REAL,
    convexity REAL
);

CREATE TABLE portfolio_holdings (
    security_id INTEGER,
    asset_class TEXT,
    market_value REAL,
    FOREIGN KEY (security_id) REFERENCES securities(id)
);

CREATE TABLE target_allocation (
    asset_class TEXT PRIMARY KEY,
    target_allocation_pct REAL
);

CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    security_id INTEGER,
    trade_date TEXT,
    day_pnl REAL,
    FOREIGN KEY (security_id) REFERENCES securities(id)
);
''')

# Insert sample data
securities = [
    (1, 'BNS.TO', 'Bank of Nova Scotia', 'Financials', 'Equity', 0, 0),
    (2, 'TD.TO', 'Toronto Dominion Bank', 'Financials', 'Equity', 0, 0),
    (3, 'SHOP.TO', 'Shopify Inc.', 'Technology', 'Equity', 0, 0),
    (4, 'BCE.TO', 'BCE Inc.', 'Communications', 'Equity', 0, 0),
    (5, 'CNR.TO', 'Canadian National Railway', 'Industrials', 'Equity', 0, 0),
    (6, 'XBB.TO', 'Canadian Bond Aggregate ETF', 'Fixed Income', 'Fixed Income', 6.5, 65.0),
    (7, 'ZAG.TO', 'BMO Aggregate Bond Index ETF', 'Fixed Income', 'Fixed Income', 7.2, 72.0),
]

portfolio = [
    (1, 'Equity', 25000), (2, 'Equity', 30000), (3, 'Equity', 15000),
    (4, 'Equity', 10000), (5, 'Equity', 20000), (6, 'Fixed Income', 35000),
    (7, 'Fixed Income', 25000),
]

target = [
    ('Equity', 60.0), ('Fixed Income', 30.0), ('Cash', 10.0),
]

# Generate sample trade data
import random
import datetime

trades = []
start = datetime.date(2025, 1, 1)
for i in range(500):
    sid = random.randint(1, 7)
    day = start + datetime.timedelta(days=random.randint(0, 365))
    pnl = round(random.uniform(-500, 500), 2)
    trades.append((i+1, sid, day.isoformat(), pnl))

cur.executemany('INSERT INTO securities VALUES (?,?,?,?,?,?,?)', securities)
cur.executemany('INSERT INTO portfolio_holdings VALUES (?,?,?)', portfolio)
cur.executemany('INSERT INTO target_allocation VALUES (?,?)', target)
cur.executemany('INSERT INTO trades VALUES (?,?,?,?)', trades)
conn.commit()

# Run all queries
queries = {
    "1. Portfolio Holdings by Asset Class": '''
        SELECT asset_class, COUNT(security_id) AS num_holdings,
               SUM(market_value) AS total_value,
               ROUND(100.0 * SUM(market_value) / (SELECT SUM(market_value) FROM portfolio_holdings), 2) AS allocation_pct
        FROM portfolio_holdings GROUP BY asset_class ORDER BY total_value DESC
    ''',
    "2. Daily P&L by Sector": '''
        SELECT sector, ROUND(SUM(day_pnl), 2) AS total_pnl,
               ROUND(AVG(day_pnl), 2) AS avg_daily_pnl
        FROM trades JOIN securities ON trades.security_id = securities.id
        WHERE trade_date >= '2025-06-01'
        GROUP BY sector ORDER BY total_pnl DESC
    ''',
    "3. Top 5 Best Performers": '''
        SELECT s.ticker, s.name, s.sector,
               ROUND(SUM(t.day_pnl), 2) AS total_pnl
        FROM trades t JOIN securities s ON t.security_id = s.id
        GROUP BY s.ticker ORDER BY total_pnl DESC LIMIT 5
    ''',
    "4. Risk: Volatility by Asset Class": '''
        SELECT p.asset_class,
               ROUND(AVG(t.day_pnl * t.day_pnl) - AVG(t.day_pnl) * AVG(t.day_pnl), 4) AS variance,
               ROUND(SQRT(ABS(AVG(t.day_pnl * t.day_pnl) - AVG(t.day_pnl) * AVG(t.day_pnl))), 4) AS daily_volatility,
               ROUND(MAX(t.day_pnl), 2) AS max_gain,
               ROUND(MIN(t.day_pnl), 2) AS max_loss
        FROM trades t JOIN portfolio_holdings p ON t.security_id = p.security_id
        GROUP BY p.asset_class
    ''',
    "5. Rebalancing Drift": '''
        WITH current AS (
            SELECT asset_class, SUM(market_value) AS cur_val,
                   100.0 * SUM(market_value) / (SELECT SUM(market_value) FROM portfolio_holdings) AS cur_pct
            FROM portfolio_holdings GROUP BY asset_class
        )
        SELECT c.asset_class, ROUND(c.cur_pct, 2) AS current_pct,
               t.target_allocation_pct,
               ROUND(c.cur_pct - t.target_allocation_pct, 2) AS drift_pct,
               CASE WHEN ABS(c.cur_pct - t.target_allocation_pct) > 2 THEN 'Rebalance Needed' ELSE 'Within Tolerance' END AS action
        FROM current c JOIN target_allocation t ON c.asset_class = t.asset_class
    ''',
    "6. Yield Impact on Bond Holdings": '''
        SELECT s.ticker, p.market_value, s.duration,
               ROUND(-s.duration * 0.01 * p.market_value, 2) AS loss_1pct_yield,
               ROUND(0.5 * s.convexity * 0.0001 * p.market_value, 2) AS convexity_adj,
               ROUND(-s.duration * 0.01 * p.market_value + 0.5 * s.convexity * 0.0001 * p.market_value, 2) AS total_impact
        FROM portfolio_holdings p JOIN securities s ON p.security_id = s.id
        WHERE s.asset_class = 'Fixed Income'
    '''
}

for name, sql in queries.items():
    print(f"\n=== {name} ===")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))

conn.close()
print("\nAll queries completed successfully.")
