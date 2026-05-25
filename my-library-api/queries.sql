-- Schema reference:
--   users(id, name, email, created_at)
--   products(id, name, category, price, stock)
--   orders(id, user_id, created_at, total_amount)
--   order_items(id, order_id, product_id, quantity, unit_price)

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 1: Top 5 users with the highest revenue in the last 3 months
-- Sums total_amount from orders placed within the last 3 months per user,
-- then returns the top 5 ranked by descending revenue.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
	u.id,
	u.name,
	u.email,
	SUM(o.total_amount) AS total_revenue
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.created_at >= NOW() - INTERVAL '3 months'
GROUP BY u.id, u.name, u.email
ORDER BY total_revenue DESC
LIMIT 5;


-- ─────────────────────────────────────────────────────────────────────────────
-- Query 2: Products that have never been purchased
-- Uses a LEFT JOIN to find products with no matching rows in order_items,
-- i.e. products that have never appeared in any order.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
	p.id,
	p.name,
	p.category,
	p.price,
	p.stock
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.id
WHERE oi.id IS NULL;


-- ─────────────────────────────────────────────────────────────────────────────
-- Query 3: Monthly revenue per category (last 6 months) — using a window function
-- Calculates each category's monthly revenue and adds a running total per category
-- using SUM as a window function ordered by month.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
	p.category,
	DATE_TRUNC('month', o.created_at)               AS month,
	SUM(oi.quantity * oi.unit_price)                AS monthly_revenue,
	SUM(SUM(oi.quantity * oi.unit_price)) OVER (
		PARTITION BY p.category
		ORDER BY DATE_TRUNC('month', o.created_at)
	)                                               AS running_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id
WHERE o.created_at >= NOW() - INTERVAL '6 months'
GROUP BY p.category, DATE_TRUNC('month', o.created_at)
ORDER BY p.category, month;


-- ─────────────────────────────────────────────────────────────────────────────
-- Query 4: Users who placed an order in January but not in February
-- Finds users with at least one order in January of the current year who have
-- no orders in February of the same year.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DISTINCT
	u.id,
	u.name,
	u.email
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE DATE_PART('month', o.created_at) = 1          -- ordered in January
  AND DATE_PART('year',  o.created_at) = DATE_PART('year', NOW())
  AND u.id NOT IN (
	  SELECT o2.user_id
	  FROM orders o2
	  WHERE DATE_PART('month', o2.created_at) = 2   -- but NOT in February
		AND DATE_PART('year',  o2.created_at) = DATE_PART('year', NOW())
  );
