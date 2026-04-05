# Dashboard screenshots

PNG files referenced by the root `README.md`:

| Filename | Content |
|----------|---------|
| `main-dashboard.png` | Overview: KPIs, filters, model accuracy |
| `transactions.png` | Transaction table: risk scores, Fraud / Legit |
| `decision-simulator.png` | Decision Simulator: threshold slider, blocked / saved revenue |
| `business-analytics.png` | Business Analytics tab: precision, recall, F1, conversion donut |
| `financial-impact.png` | Financial Impact tab: chargeback cost, net benefit |

To update screenshots after UI changes:

```bash
git add docs/screenshots/*.png README.md
git commit -m "docs: refresh dashboard screenshots"
```
