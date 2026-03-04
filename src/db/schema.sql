PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS wallets (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	base_currency TEXT NOT NULL DEFAULT 'USD',
	created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	wallet_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	category TEXT NOT NULL CHECK (
		category IN (
			'bank_deposit', 'digital_asset', 'stock', 'etf', 'mutual_fund',
			'bond', 'real_estate', 'commodity', 'cash', 'other'
		)
	),
	currency TEXT NOT NULL DEFAULT 'USD',
	tags TEXT,
	institution TEXT,
	account_number_masked TEXT,
	symbol TEXT,
	ticker TEXT,
	exchange TEXT,
	quantity REAL,
	spot_price REAL,
	market_price REAL,
	nav_or_market_price REAL,
	expense_ratio REAL,
	issuer TEXT,
	face_value REAL,
	market_value REAL,
	coupon_rate REAL,
	maturity_date TEXT,
	location TEXT,
	estimated_market_value REAL,
	ownership_share REAL,
	amount REAL,
	notes TEXT,
	created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS liabilities (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	wallet_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	category TEXT NOT NULL CHECK (
		category IN ('mortgage', 'loan', 'credit_card', 'tax', 'other')
	),
	principal REAL NOT NULL,
	outstanding_balance REAL NOT NULL,
	annual_interest_rate REAL NOT NULL DEFAULT 0,
	minimum_payment REAL NOT NULL DEFAULT 0,
	due_date TEXT,
	lender TEXT,
	currency TEXT NOT NULL DEFAULT 'USD',
	tags TEXT,
	created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS incomes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	wallet_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	income_type TEXT NOT NULL CHECK (
		income_type IN ('salary', 'bonus', 'freelance', 'dividend', 'interest', 'rental', 'business', 'other')
	),
	amount REAL NOT NULL,
	frequency TEXT NOT NULL CHECK (
		frequency IN ('once', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly')
	),
	source TEXT,
	currency TEXT NOT NULL DEFAULT 'USD',
	is_taxable INTEGER NOT NULL DEFAULT 1 CHECK (is_taxable IN (0, 1)),
	created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS expenses (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	wallet_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	category TEXT NOT NULL CHECK (
		category IN (
			'housing', 'transport', 'food', 'healthcare', 'insurance',
			'education', 'entertainment', 'debt_payment', 'investment', 'other'
		)
	),
	amount REAL NOT NULL,
	frequency TEXT NOT NULL CHECK (
		frequency IN ('once', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly')
	),
	vendor TEXT,
	currency TEXT NOT NULL DEFAULT 'USD',
	essential INTEGER NOT NULL DEFAULT 1 CHECK (essential IN (0, 1)),
	created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cash_flows (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	wallet_id INTEGER NOT NULL,
	event_date TEXT NOT NULL,
	flow_type TEXT NOT NULL CHECK (flow_type IN ('inflow', 'outflow', 'transfer')),
	amount REAL NOT NULL,
	description TEXT,
	category TEXT,
	currency TEXT NOT NULL DEFAULT 'USD',
	related_asset_name TEXT,
	created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_assets_wallet_id ON assets(wallet_id);
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category);
CREATE INDEX IF NOT EXISTS idx_liabilities_wallet_id ON liabilities(wallet_id);
CREATE INDEX IF NOT EXISTS idx_incomes_wallet_id ON incomes(wallet_id);
CREATE INDEX IF NOT EXISTS idx_expenses_wallet_id ON expenses(wallet_id);
CREATE INDEX IF NOT EXISTS idx_cash_flows_wallet_id ON cash_flows(wallet_id);
CREATE INDEX IF NOT EXISTS idx_cash_flows_event_date ON cash_flows(event_date);
