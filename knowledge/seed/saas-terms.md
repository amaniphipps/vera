# SaaS terms - shared glossary (seed)

Canonical SaaS vocabulary, shipped with Vera. This is generic industry
knowledge, not org-specific truth - org terms still belong in
`knowledge/graph/entities/glossary/`, which Vera builds per deployment.
Use these definitions when answering, and copy a term into the org glossary
when the org uses it in a specific way.

## Revenue metrics

- **ARR (annual recurring revenue)** - predictable subscription revenue over a
  year. The headline health metric for a subscription business.
- **MRR (monthly recurring revenue)** - the monthly slice of recurring
  revenue. Sum of all active subscription value, excluding one-time charges.
- **ARPPU (average revenue per paying user)** - revenue from paying users
  divided by the count of paying users in a period. Excludes free and trial
  users.
- **CLTV (customer lifetime value)** - total revenue expected from a customer
  over the whole relationship. Read against CAC: the ratio tells you whether
  acquisition economics work.
- **CAC (customer acquisition cost)** - everything spent on sales and
  marketing to win one new customer: campaigns, salaries, commissions, tools.
- **Churn rate** - share of customers (or revenue) lost in a period, divided
  by the starting count. Logo churn counts customers; revenue churn counts
  dollars. Say which one you mean.
- **Renewal rate** - share of customers up for renewal who renew.
- **Customer retention rate** - share of customers still active after a
  period. The mirror of churn.
- **Net revenue retention (NRR/NDR)** - starting cohort revenue plus
  expansion, minus contraction and churn, over the period. Above 100% means
  the base grows without new sales. (Added beyond the source list.)
- **Gross revenue retention (GRR)** - same but excluding expansion. The floor
  of the business. (Added.)
- **Payback period** - months of gross margin needed to earn back CAC.
  (Added.)

## Customers

- **Customer success** - the discipline of driving retention, expansion, and
  advocacy by making customers measurably successful, not just supported.
- **Customer satisfaction (CSAT)** - how well the product and the company meet
  expectations, usually survey-measured.
- **NPS (net promoter score)** - % promoters (9–10) minus % detractors (0–6)
  on the "would you recommend us" question.
- **Customer segmentation** - grouping customers by shared traits so messaging
  and motion can differ by group.
- **Customer journey mapping** - the end-to-end picture of a customer's
  touchpoints, from first awareness through onboarding and steady use.
- **Customer feedback loop** - the continuous cycle of collecting, reading,
  and acting on customer input.
- **Cohort analysis** - tracking a group that shares a start point (signup
  month, plan, feature) over time to see how behavior and retention move.
- **Onboarding support tickets per day** - ticket volume during new-customer
  onboarding; a friction signal for time-to-value.

## Growth and go-to-market

- **GTM (go-to-market)** - the coordinated plan across sales, marketing, and
  distribution to reach and win customers.
- **Growth hacking** - data-driven, experiment-heavy pursuit of fast growth.
  The AARRR funnel (acquisition, activation, retention, referral, revenue) is
  the classic frame.
- **Inbound marketing** - winning customers by being found (content, search,
  useful material) instead of interrupting them.
- **Lead generation** - identifying and capturing potential customers'
  interest and contact details.
- **Lead scoring** - ranking leads by fit and engagement so effort goes to
  the most likely buyers.
- **Conversion rate** - the share of prospects who take the desired step
  (signup, trial, purchase) at a given funnel stage.
- **Free trial conversion rate** - share of trial users who become paying
  customers.
- **Sales enablement** - equipping the sales team with content, training, and
  tools to sell effectively.
- **Product-led growth (PLG)** - the product itself drives acquisition and
  expansion: free tier or trial, low-friction start, self-serve onboarding.
- **Sales-led growth** - the sales team drives acquisition: outbound,
  relationships, negotiated deals.
- **Product-market fit (PMF)** - the product demonstrably solves a real
  problem for a defined market that keeps coming back.

## Product

- **MVP (minimum viable product)** - the smallest build that tests the core
  hypothesis with real users.
- **Product roadmap** - the sequenced plan of what gets built and roughly
  when, used to align the org.
- **Product adoption** - how fully intended users actually take up the
  product.
- **Feature adoption rate** - how quickly users start using a specific
  feature after release.
- **User onboarding** - the guided first-run experience that gets a new user
  to their first win.
- **Time-to-value (TTV)** - how long until a customer gets real, tangible
  value. Shorter is the whole game in onboarding.
- **User story** - a short narrative of what a user needs to do and why, used
  to frame product work.
- **UAT (user acceptance testing)** - end users validating that the product
  works for them before release.
- **UX (user experience)** - the overall quality of using the product:
  design, navigation, responsiveness, feel.
- **MAU (monthly active users)** - users who did something meaningful in the
  product in a month. DAU/WAU are the daily/weekly cousins; the DAU/MAU ratio
  reads stickiness.

## Pricing and business models

- **Subscription model** - recurring fee (monthly or annual) for ongoing
  access, hosted by the provider.
- **Billing cycle** - how often customers are invoiced: monthly, quarterly,
  annually.
- **Freemium** - a genuinely free tier alongside paid plans; the free base is
  the acquisition engine.
- **Usage-based pricing** - customers pay for what they consume, not a flat
  fee.
- **Upselling** - growing existing customers into higher tiers or add-ons.
- **Bootstrapping** - funding the company from its own revenue, keeping
  ownership and control.
- **Self-service** - users can buy, set up, and manage the product without
  talking to anyone.
- **Scalability** - the product's ability to grow load without degrading.

## Category terms

- **API (application programming interface)** - the contract other software
  uses to read and write a system: endpoints, auth, data shapes.
- **PaaS (platform as a service)** - a hosted platform for building and
  running applications without owning the infrastructure.
- **Horizontal SaaS** - serves many industries with a flexible, general
  product.
- **Vertical SaaS** - purpose-built for one industry's specific needs.
- **In-app messaging** - communication inside the product itself, not over
  email or external chat.

---
Source list adapted from designwithvalue.com/saas-terms (50 terms), with
RevOps additions (NRR, GRR, payback period) that the analysis skills need
daily. Definitions are Vera's own phrasing.
