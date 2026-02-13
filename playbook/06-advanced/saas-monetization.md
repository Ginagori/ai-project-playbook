# SaaS Monetization Guide

A comprehensive guide for monetizing SaaS products with AI agents — pricing models, Stripe integration, token billing, marketplace commission, and cost optimization.

## Pricing Models Overview

| Model | Best For | Example | Complexity |
|-------|----------|---------|------------|
| **Flat subscription** | Simple SaaS | $49/mo for full access | Low |
| **Token-based** | API/AI-heavy | $0.01 per 1K tokens | Medium |
| **Per-agent/seat** | Multi-agent platforms | $29/agent/month | Medium |
| **Marketplace commission** | Agent stores | 20% on agent sales | High |
| **Hybrid** | Full platforms | Base sub + tokens + commission | High |

### Tier Design

```
Free        →  $0/mo     100 tokens, 1 agent, basic features
Starter     →  $29/mo    5,000 tokens, 3 agents, standard features
Pro         →  $99/mo    25,000 tokens, 10 agents, advanced features
Enterprise  →  $499+/mo  Unlimited tokens, unlimited agents, custom SLA
```

### Cost Calculation

```
cost_per_user = (avg_api_calls × cost_per_call) + (infra_cost / total_users)

Example:
- Average user makes 500 AI calls/month
- Cost per call (Claude Sonnet): ~$0.006
- API cost per user: 500 × $0.006 = $3.00
- Infrastructure per user: $12,000 / 1,000 users = $12.00
- Total cost per user: $15.00
- Price at 3x margin: $45/month → round to $49
```

---

## Stripe Integration

### Core Concepts

| Stripe Object | Purpose |
|---------------|---------|
| **Customer** | Represents a user in Stripe |
| **Product** | What you're selling (your SaaS plans) |
| **Price** | How much it costs (monthly, annually) |
| **Subscription** | Recurring payment for a Price |
| **PaymentIntent** | One-time payment |
| **Webhook** | Stripe notifying your server of events |

### Setup

```python
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
```

### Creating Products and Prices

```python
# Create in Stripe Dashboard or via API (one-time setup)
product = stripe.Product.create(
    name="Pro Plan",
    description="25,000 tokens, 10 agents, advanced features",
)

# Monthly price
monthly_price = stripe.Price.create(
    product=product.id,
    unit_amount=9900,  # $99.00 in cents!
    currency="usd",
    recurring={"interval": "month"},
)

# Annual price (with discount)
annual_price = stripe.Price.create(
    product=product.id,
    unit_amount=95000,  # $950/year (~$79/mo)
    currency="usd",
    recurring={"interval": "year"},
)
```

### Creating Customers and Subscriptions

```python
async def create_subscription(user_id: str, email: str, price_id: str):
    """Create a Stripe subscription for a user."""
    # 1. Create or get customer
    customer = stripe.Customer.create(
        email=email,
        metadata={"user_id": str(user_id)},
    )

    # 2. Create checkout session (redirects user to Stripe)
    session = stripe.checkout.Session.create(
        customer=customer.id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{APP_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{APP_URL}/pricing",
        metadata={"user_id": str(user_id)},
    )

    return session.url  # Redirect user here
```

### Webhook Handling

```python
from fastapi import Request, HTTPException

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    # CRITICAL: Always verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    # Handle events
    match event["type"]:
        case "checkout.session.completed":
            await handle_checkout_completed(event["data"]["object"])
        case "invoice.paid":
            await handle_invoice_paid(event["data"]["object"])
        case "customer.subscription.updated":
            await handle_subscription_updated(event["data"]["object"])
        case "customer.subscription.deleted":
            await handle_subscription_canceled(event["data"]["object"])
        case "invoice.payment_failed":
            await handle_payment_failed(event["data"]["object"])

    return {"status": "ok"}


async def handle_checkout_completed(session: dict):
    """User completed checkout — activate subscription."""
    user_id = session["metadata"]["user_id"]
    subscription_id = session["subscription"]

    sub = stripe.Subscription.retrieve(subscription_id)
    price_id = sub["items"]["data"][0]["price"]["id"]

    # Map Stripe price to your tier
    tier = PRICE_TO_TIER.get(price_id, "starter")

    await db.execute("""
        UPDATE users SET
            subscription_tier = $1,
            stripe_customer_id = $2,
            stripe_subscription_id = $3,
            token_balance = token_balance + $4
        WHERE id = $5
    """, tier, session["customer"], subscription_id,
        TIER_TOKENS[tier], user_id)


async def handle_subscription_canceled(subscription: dict):
    """Subscription canceled — downgrade to free."""
    customer_id = subscription["customer"]
    await db.execute("""
        UPDATE users SET
            subscription_tier = 'free',
            stripe_subscription_id = NULL
        WHERE stripe_customer_id = $1
    """, customer_id)
```

---

## Token Billing (Atomic Operations)

### Why Atomic Operations Matter

Without atomicity, concurrent API calls can over-deduct tokens:

```
User balance: 100 tokens
Thread A reads: 100 tokens → deducts 80 → writes 20
Thread B reads: 100 tokens → deducts 80 → writes 20  (RACE CONDITION!)
Expected: 100 - 80 - 80 = error (insufficient)
Actual: Both succeed, user got 160 tokens worth of service for 100
```

### PostgreSQL Atomic Deduction

```sql
CREATE OR REPLACE FUNCTION deduct_tokens(
    p_user_id UUID,
    p_amount INTEGER,
    p_description TEXT,
    p_event_id TEXT DEFAULT NULL
) RETURNS TABLE(success BOOLEAN, remaining INTEGER, transaction_id UUID)
LANGUAGE plpgsql AS $$
DECLARE
    v_current_balance INTEGER;
    v_transaction_id UUID;
BEGIN
    -- Idempotency check (prevents duplicate deductions)
    IF p_event_id IS NOT NULL THEN
        IF EXISTS (SELECT 1 FROM token_transactions WHERE event_id = p_event_id) THEN
            RETURN QUERY
                SELECT true, (SELECT token_balance FROM users WHERE id = p_user_id),
                       (SELECT id FROM token_transactions WHERE event_id = p_event_id);
            RETURN;
        END IF;
    END IF;

    -- Lock the row and read balance atomically
    SELECT token_balance INTO v_current_balance
    FROM users WHERE id = p_user_id
    FOR UPDATE;

    -- Check sufficient balance
    IF v_current_balance IS NULL THEN
        RETURN QUERY SELECT false, 0, NULL::UUID;
        RETURN;
    END IF;

    IF v_current_balance < p_amount THEN
        RETURN QUERY SELECT false, v_current_balance, NULL::UUID;
        RETURN;
    END IF;

    -- Deduct
    UPDATE users
    SET token_balance = token_balance - p_amount
    WHERE id = p_user_id;

    -- Record transaction
    INSERT INTO token_transactions (user_id, amount, type, description, event_id)
    VALUES (p_user_id, -p_amount, 'deduction', p_description, p_event_id)
    RETURNING id INTO v_transaction_id;

    RETURN QUERY SELECT true, v_current_balance - p_amount, v_transaction_id;
END;
$$;
```

### Token Addition (After Payment)

```sql
CREATE OR REPLACE FUNCTION add_tokens(
    p_user_id UUID,
    p_amount INTEGER,
    p_description TEXT,
    p_event_id TEXT DEFAULT NULL
) RETURNS TABLE(success BOOLEAN, new_balance INTEGER, transaction_id UUID)
LANGUAGE plpgsql AS $$
DECLARE
    v_transaction_id UUID;
    v_new_balance INTEGER;
BEGIN
    -- Idempotency check
    IF p_event_id IS NOT NULL THEN
        IF EXISTS (SELECT 1 FROM token_transactions WHERE event_id = p_event_id) THEN
            RETURN QUERY
                SELECT true, (SELECT token_balance FROM users WHERE id = p_user_id),
                       (SELECT id FROM token_transactions WHERE event_id = p_event_id);
            RETURN;
        END IF;
    END IF;

    -- Add tokens
    UPDATE users
    SET token_balance = token_balance + p_amount
    WHERE id = p_user_id
    RETURNING token_balance INTO v_new_balance;

    -- Record transaction
    INSERT INTO token_transactions (user_id, amount, type, description, event_id)
    VALUES (p_user_id, p_amount, 'purchase', p_description, p_event_id)
    RETURNING id INTO v_transaction_id;

    RETURN QUERY SELECT true, v_new_balance, v_transaction_id;
END;
$$;
```

### Python Integration

```python
async def use_tokens(user_id: str, amount: int, description: str,
                     event_id: str | None = None) -> bool:
    """Deduct tokens atomically. Returns True if successful."""
    result = await db.fetch_one(
        "SELECT * FROM deduct_tokens($1, $2, $3, $4)",
        user_id, amount, description, event_id,
    )
    return result["success"]

# Usage in agent endpoint
@app.post("/api/agent/chat")
async def agent_chat(request: ChatRequest, user: User = Depends(get_current_user)):
    # Estimate token cost
    estimated_cost = estimate_tokens(request.message)

    # Deduct tokens before processing
    event_id = f"chat_{request.conversation_id}_{uuid.uuid4()}"
    if not await use_tokens(user.id, estimated_cost, "agent_chat", event_id):
        raise HTTPException(402, "Insufficient tokens")

    # Process request
    response = await agent.run(request.message)

    # Adjust for actual usage (refund or charge extra)
    actual_cost = count_tokens(response)
    diff = estimated_cost - actual_cost
    if diff > 0:
        await add_tokens(user.id, diff, "refund_overestimate")

    return response
```

---

## Database Schema

```sql
-- Users with billing
ALTER TABLE users ADD COLUMN IF NOT EXISTS token_balance INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier TEXT DEFAULT 'free';

-- Token transactions
CREATE TABLE IF NOT EXISTS token_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('purchase', 'deduction', 'bonus', 'refund')),
    description TEXT,
    event_id TEXT UNIQUE,  -- For idempotency
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_transactions_user ON token_transactions(user_id);
CREATE INDEX idx_transactions_created ON token_transactions(created_at);
CREATE INDEX idx_transactions_event ON token_transactions(event_id) WHERE event_id IS NOT NULL;

-- RLS
ALTER TABLE token_transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own transactions" ON token_transactions
    FOR SELECT USING (auth.uid() = user_id);
```

---

## Real-Time Balance (Supabase)

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Subscribe to balance changes
function useTokenBalance(userId: string) {
  const [balance, setBalance] = useState<number>(0)

  useEffect(() => {
    // Initial fetch
    supabase
      .from('users')
      .select('token_balance')
      .eq('id', userId)
      .single()
      .then(({ data }) => setBalance(data?.token_balance ?? 0))

    // Real-time subscription
    const channel = supabase
      .channel('balance')
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'users',
        filter: `id=eq.${userId}`,
      }, (payload) => {
        setBalance(payload.new.token_balance)
      })
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [userId])

  return balance
}
```

---

## Frontend Components

### Pricing Card

```typescript
interface PricingTier {
  name: string
  price: number
  tokens: number
  features: string[]
  priceId: string
  popular?: boolean
}

function PricingCard({ tier }: { tier: PricingTier }) {
  const handleSubscribe = async () => {
    const response = await fetch('/api/billing/create-checkout', {
      method: 'POST',
      body: JSON.stringify({ priceId: tier.priceId }),
    })
    const { url } = await response.json()
    window.location.href = url  // Redirect to Stripe Checkout
  }

  return (
    <div className={`pricing-card ${tier.popular ? 'popular' : ''}`}>
      <h3>{tier.name}</h3>
      <div className="price">${tier.price}/mo</div>
      <div className="tokens">{tier.tokens.toLocaleString()} tokens/mo</div>
      <ul>
        {tier.features.map(f => <li key={f}>{f}</li>)}
      </ul>
      <button onClick={handleSubscribe}>
        {tier.popular ? 'Get Started' : 'Subscribe'}
      </button>
    </div>
  )
}
```

### Token Balance Display

```typescript
function TokenBalance({ userId }: { userId: string }) {
  const balance = useTokenBalance(userId)
  const percentage = (balance / MAX_TOKENS) * 100

  return (
    <div className="token-balance">
      <span>{balance.toLocaleString()} tokens remaining</span>
      <div className="progress-bar">
        <div
          className={`fill ${percentage < 20 ? 'warning' : ''}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {percentage < 20 && (
        <a href="/billing/add-tokens">Low balance — add more tokens</a>
      )}
    </div>
  )
}
```

---

## Critical Gotchas

| Gotcha | Impact | Prevention |
|--------|--------|------------|
| **Race conditions in token deduction** | Users get free service | Use `FOR UPDATE` in PostgreSQL |
| **Webhook duplicate events** | Double-charge or double-credit | Use `event_id` for idempotency |
| **Amounts in cents** | $49.99 → must send 4999 | Always convert: `int(price * 100)` |
| **Skipping webhook signature** | Attackers send fake events | ALWAYS verify `stripe-signature` |
| **Test vs live keys** | Charges real cards in dev | Check key prefix: `sk_test_` vs `sk_live_` |
| **Subscription state machine** | User access after cancellation | Handle: active → past_due → canceled |
| **Missing error handling** | Silent failures | Log every webhook, alert on failures |
| **Not handling `past_due`** | User still has access after failed payment | Downgrade after grace period |

### Stripe Key Safety

```python
# In your startup validation
stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
if stripe_key.startswith("sk_live_") and os.getenv("ENVIRONMENT") != "production":
    raise ValueError("DANGER: Live Stripe key in non-production environment!")
```

---

## Marketplace Commission Model

For platforms where third-party creators sell agents:

### Stripe Connect

```python
# Onboard creator as connected account
account = stripe.Account.create(
    type="express",
    email=creator.email,
    metadata={"creator_id": str(creator.id)},
)

# Create account link for onboarding
link = stripe.AccountLink.create(
    account=account.id,
    refresh_url=f"{APP_URL}/creators/onboard",
    return_url=f"{APP_URL}/creators/dashboard",
    type="account_onboarding",
)
# Redirect creator to link.url

# When user buys an agent, split the payment
payment_intent = stripe.PaymentIntent.create(
    amount=2900,  # $29.00
    currency="usd",
    application_fee_amount=580,  # 20% platform fee = $5.80
    transfer_data={"destination": creator.stripe_account_id},
)
```

---

## Pricing Strategy

### Cost-Plus Pricing

```
price = total_cost × (1 + target_margin)

Example for Pro tier:
- API costs: $3/user/month
- Infrastructure: $12/user/month
- Support: $5/user/month
- Total cost: $20/user/month
- Target margin: 4x
- Price: $80 → round to $99/month
```

### Free Tier with Token Limits

```python
TIER_CONFIG = {
    "free": {
        "tokens_per_month": 100,
        "max_agents": 1,
        "features": ["basic_chat"],
    },
    "starter": {
        "tokens_per_month": 5000,
        "max_agents": 3,
        "features": ["basic_chat", "file_upload", "export"],
    },
    "pro": {
        "tokens_per_month": 25000,
        "max_agents": 10,
        "features": ["basic_chat", "file_upload", "export", "api_access", "custom_agents"],
    },
}
```

### Overage Handling

| Strategy | Behavior | Best For |
|----------|----------|----------|
| **Block** | Stop service at limit | Free tier |
| **Throttle** | Slow down responses | Starter tier |
| **Charge** | Auto-buy more tokens | Pro/Enterprise |

```python
async def check_token_limit(user: User) -> str:
    if user.token_balance > 0:
        return "ok"

    tier = TIER_CONFIG[user.subscription_tier]
    overage = tier.get("overage_strategy", "block")

    match overage:
        case "block":
            raise HTTPException(402, "Token limit reached. Upgrade to continue.")
        case "throttle":
            await asyncio.sleep(5)  # Artificial delay
            return "throttled"
        case "charge":
            await auto_purchase_tokens(user, amount=1000)
            return "ok"
```

---

## Monetization Checklist

### Foundation
- [ ] Stripe account created (test + live keys)
- [ ] Products and Prices configured
- [ ] Webhook endpoint with signature verification
- [ ] Token balance column on users table
- [ ] Atomic token deduction function

### Billing Flow
- [ ] Checkout session creation
- [ ] Subscription lifecycle handling (created, updated, canceled)
- [ ] Invoice payment success/failure handling
- [ ] Token addition on successful payment

### Frontend
- [ ] Pricing page with tier comparison
- [ ] Checkout redirect to Stripe
- [ ] Success/cancel pages
- [ ] Token balance display (real-time)
- [ ] Billing portal link (manage subscription)

### Production
- [ ] Idempotency on all token operations
- [ ] Live key safety checks
- [ ] Webhook retry handling
- [ ] Cost monitoring and alerts
- [ ] Revenue reporting dashboard
