"""Generates a short, plain-language stakeholder summary (Markdown) from the
computed KPIs — the kind of write-up that would go out after a monthly
process governance review."""
from datetime import datetime


def generate_summary(frames, status_df, approval_df, cycle_df, provider_df, change_df, breaches_df, output_path):
    total_requests = len(frames["requests"])
    total_offers = len(frames["offers"])
    total_orders = len(frames["orders"])
    approval_rate_pct = approval_df["approval_rate_pct"].iloc[0]
    top_status = status_df.iloc[0]
    slowest_stage = cycle_df.loc[cycle_df["avg_days"].idxmax()]
    top_provider = provider_df.iloc[0] if not provider_df.empty else None
    n_breaches = len(breaches_df)

    lines = []
    lines.append(f"# IT Service Management — Monthly Process Summary")
    lines.append(f"_Generated {datetime.now().strftime('%Y-%m-%d')}_\n")

    lines.append("## Headline")
    lines.append(
        f"- **{total_requests}** service requests processed, generating **{total_offers}** provider offers "
        f"and **{total_orders}** orders placed.\n"
        f"- Procurement approval rate stands at **{approval_rate_pct}%**.\n"
        f"- The most common current status is **{top_status['status']}** "
        f"({top_status['pct_of_total']}% of all requests).\n"
    )

    lines.append("## Process Cycle Time")
    lines.append(
        f"- Slowest stage: **{slowest_stage['stage']}**, averaging **{slowest_stage['avg_days']} days** "
        f"(max observed: {slowest_stage['max_days']} days).\n"
    )
    for _, row in cycle_df.iterrows():
        lines.append(f"  - {row['stage']}: avg {row['avg_days']}d, max {row['max_days']}d")
    lines.append("")

    lines.append("## Control Deviations")
    if n_breaches:
        lines.append(f"- **{n_breaches} requests** exceeded the 7-day review SLA for Procurement approval.")
        lines.append("  Top offenders:")
        for _, row in breaches_df.head(5).iterrows():
            lines.append(
                f"  - Request #{int(row['request_id'])} \"{row['title']}\" "
                f"({row['department']}, PM: {row['project_manager']}) — "
                f"{row['review_to_approval_days']:.1f} days"
            )
    else:
        lines.append("- No SLA breaches detected in the review-to-approval stage this period.")
    lines.append("")

    lines.append("## Provider Performance")
    if top_provider is not None:
        lines.append(
            f"- Top performer by win rate: **{top_provider['provider_name']}** "
            f"({top_provider['win_rate_pct']}% win rate, avg evaluation score {top_provider['avg_score']}).\n"
        )
    for _, row in provider_df.iterrows():
        lines.append(
            f"  - {row['provider_name']}: {row['offers_submitted']} offers submitted, "
            f"{int(row['orders_won'])} won, {row['win_rate_pct']}% win rate, avg score {row['avg_score']}"
        )
    lines.append("")

    lines.append("## Change Requests")
    if not change_df.empty:
        for _, row in change_df.iterrows():
            lines.append(
                f"- {row['change_type'].title()}: {int(row['count'])} requested, "
                f"{row['approval_rate_pct']}% approved, avg resolution {row['avg_resolution_days']} days"
            )
    else:
        lines.append("- No order change requests (substitutions/extensions) recorded this period.")
    lines.append("")

    lines.append("## Recommended Follow-ups")
    recs = []
    if n_breaches > total_requests * 0.1:
        recs.append("Investigate root cause of SLA breaches in Procurement review — over 10% of requests are affected.")
    if slowest_stage["stage"].startswith("Bidding"):
        recs.append("Review whether default bidding windows are longer than necessary for low-complexity requests.")
    if top_provider is not None and top_provider["win_rate_pct"] < 20:
        recs.append("No single provider dominates bidding — healthy competitive spread, worth monitoring for consolidation risk.")
    if not recs:
        recs.append("No urgent action items; continue standard monitoring cadence.")
    for rec in recs:
        lines.append(f"- {rec}")

    text = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(text)
    return output_path
