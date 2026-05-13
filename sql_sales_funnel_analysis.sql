/*
  SQL Case Study — Sales Funnel Analysis
  Author: Mohamed Lamkadmi
  Description: Business queries analyzing customer conversion patterns 
  using a sample e-commerce dataset. Demonstrates CTEs, window functions, 
  joins, and aggregate analysis.
*/

-- 1. Monthly conversion rate trend
WITH monthly_visits AS (
    SELECT 
        DATE_TRUNC('month', visit_date) AS month,
        COUNT(DISTINCT visitor_id) AS total_visitors,
        COUNT(DISTINCT CASE WHEN purchased = TRUE THEN visitor_id END) AS purchasers
    FROM sales_data
    GROUP BY DATE_TRUNC('month', visit_date)
)
SELECT 
    month,
    total_visitors,
    purchasers,
    ROUND(100.0 * purchasers / NULLIF(total_visitors, 0), 2) AS conversion_rate
FROM monthly_visits
ORDER BY month;

-- 2. Top 10% customers by revenue (window function)
WITH customer_revenue AS (
    SELECT 
        customer_id,
        SUM(amount) AS total_spent,
        RANK() OVER (ORDER BY SUM(amount) DESC) AS revenue_rank
    FROM transactions
    GROUP BY customer_id
)
SELECT * FROM customer_revenue
WHERE revenue_rank <= (SELECT COUNT(*) * 0.1 FROM customer_revenue);

-- 3. Funnel drop-off by stage
SELECT 
    stage,
    COUNT(DISTINCT user_id) AS users,
    LAG(COUNT(DISTINCT user_id)) OVER (ORDER BY stage_order) AS previous_stage_users,
    ROUND(
        100.0 * (COUNT(DISTINCT user_id) - LAG(COUNT(DISTINCT user_id)) OVER (ORDER BY stage_order)) 
        / NULLIF(LAG(COUNT(DISTINCT user_id)) OVER (ORDER BY stage_order), 0), 
    2) AS drop_off_pct
FROM funnel_stages
GROUP BY stage, stage_order
ORDER BY stage_order;

-- 4. Customer segment performance
SELECT 
    segment,
    COUNT(DISTINCT customer_id) AS customer_count,
    ROUND(AVG(lifetime_value), 2) AS avg_ltv,
    ROUND(SUM(revenue), 2) AS total_revenue,
    RANK() OVER (ORDER BY SUM(revenue) DESC) AS revenue_rank
FROM customer_segments
JOIN transactions ON customer_segments.customer_id = transactions.customer_id
GROUP BY segment
ORDER BY total_revenue DESC;

-- 5. Repeat purchase behavior
SELECT 
    customer_id,
    COUNT(order_id) AS order_count,
    MIN(order_date) AS first_order,
    MAX(order_date) AS last_order,
    DATEDIFF('day', MIN(order_date), MAX(order_date)) AS customer_lifetime_days
FROM orders
GROUP BY customer_id
HAVING COUNT(order_id) > 1
ORDER BY order_count DESC;
