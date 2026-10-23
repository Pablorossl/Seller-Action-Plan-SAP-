from quality.rules import MQC_MINIMUM_ORDERS, is_monthly_period


def classify(metric):
    """Clasifica una observación mensual por canal; no ejecuta acciones en Mirakl."""
    policy = metric.policy
    if metric.value is None:
        return "not_evaluable"
    if policy.is_mqc and not is_monthly_period(metric.period_start, metric.period_end):
        return "not_evaluable"
    if policy.is_mqc and metric.order_count is None:
        return "not_evaluable"
    if policy.is_mqc and metric.order_count < max(MQC_MINIMUM_ORDERS, policy.minimum_orders):
        return "insufficient_orders"

    def exceeds(threshold):
        return metric.value < threshold if policy.operator == "lt" else metric.value >= threshold

    if policy.is_mqc and exceeds(policy.suspension):
        return "suspension_threshold"
    if exceeds(policy.alarm):
        return "alarm" if policy.is_mqc else "below_reference"
    return "ok"
