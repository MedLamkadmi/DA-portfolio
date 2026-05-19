/*
  Financial Data Analysis - SQL Case Study
  Author: Mohamed Lamkadmi
  Description: SQL queries analyzing portfolio holdings, 
  P&L calculations, and risk reporting for a sample investment portfolio.
*/

-- 1. Portfolio holdings summary by asset class
SELECT 
    asset_class,
    COUNT(security_id) AS num_holdings,
    SUM(market_value) AS total_value,
    ROUND(100.0 * SUM(market_value) / (SELECT SUM(market_value) FROM portfolio_holdings), 2) AS allocation_pct
FROM portfolio_holdings
GROUP BY asset_class
ORDER BY total_value DESC;

-- 2. Daily P&L by sector
SELECT 
    sector,
    SUM(day_pnl) AS total_pnl,
    ROUND(AVG(day_pnl), 2) AS avg_daily_pnl,
    COUNT(DISTINCT security_id) AS securities
FROM trades
JOIN securities ON trades.security_id = securities.id
WHERE trade_date >= DATEADD('month', -1, CURRENT_DATE)
GROUP BY sector
ORDER BY total_pnl DESC;

-- 3. Top 10 best and worst performers
WITH security_performance AS (
    SELECT 
        security_id,
        SUM(day_pnl) AS total_pnl,
        COUNT(trade_date) AS trading_days
    FROM trades
    WHERE trade_date >= DATEADD('quarter', -1, CURRENT_DATE)
    GROUP BY security_id
)
SELECT 
    s.ticker,
    s.name,
    s.sector,
    sp.total_pnl,
    sp.trading_days,
    ROUND(sp.total_pnl / NULLIF(sp.trading_days, 0), 2) AS avg_daily_pnl
FROM security_performance sp
JOIN securities s ON sp.security_id = s.id
ORDER BY sp.total_pnl DESC
LIMIT 10;

-- 4. Risk reporting: portfolio volatility by asset class
SELECT 
    p.asset_class,
    ROUND(STDDEV(t.day_pnl), 4) AS daily_volatility,
    ROUND(STDDEV(t.day_pnl) * SQRT(252), 4) AS annualized_volatility,
    MAX(t.day_pnl) AS max_gain,
    MIN(t.day_pnl) AS max_loss
FROM trades t
JOIN portfolio_holdings p ON t.security_id = p.security_id
WHERE t.trade_date >= DATEADD('year', -1, CURRENT_DATE)
GROUP BY p.asset_class
ORDER BY annualized_volatility DESC;

-- 5. Portfolio rebalancing needs (drift from target allocation)
WITH current_allocation AS (
    SELECT 
        asset_class,
        SUM(market_value) AS current_value,
        100.0 * SUM(market_value) / (SELECT SUM(market_value) FROM portfolio_holdings) AS current_pct
    FROM portfolio_holdings
    GROUP BY asset_class
)
SELECT 
    c.asset_class,
    c.current_value,
    ROUND(c.current_pct, 2) AS current_allocation_pct,
    t.target_allocation_pct,
    ROUND(c.current_pct - t.target_allocation_pct, 2) AS drift_pct,
    CASE 
        WHEN c.current_pct - t.target_allocation_pct > 2 THEN 'Overweight - Rebalance'
        WHEN t.target_allocation_pct - c.current_pct > 2 THEN 'Underweight - Rebalance'
        ELSE 'Within Tolerance'
    END AS rebalance_action
FROM current_allocation c
JOIN target_allocation t ON c.asset_class = t.asset_class
ORDER BY ABS(c.current_pct - t.target_allocation_pct) DESC;

-- 6. Scenario: impact of 1% yield increase on bond holdings
WITH bond_holdings AS (
    SELECT 
        p.security_id,
        s.ticker,
        p.market_value,
        s.duration,
        s.convexity
    FROM portfolio_holdings p
    JOIN securities s ON p.security_id = s.id
    WHERE s.asset_class = 'Fixed Income'
)
SELECT 
    ticker,
    market_value,
    ROUND(duration, 2) AS duration,
    ROUND(-duration * 0.01 * market_value, 2) AS estimated_loss_1pct_yield,
    ROUND(0.5 * convexity * (0.01 * 0.01) * market_value, 2) AS convexity_adjustment,
    ROUND(-duration * 0.01 * market_value + 0.5 * convexity * (0.01 * 0.01) * market_value, 2) AS total_estimated_impact
FROM bond_holdings
ORDER BY estimated_loss_1pct_yield DESC;
