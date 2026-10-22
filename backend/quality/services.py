def classify(metric):
    """Clasifica una observación mensual por canal; no ejecuta acciones en Mirakl."""
    policy = metric.policy
    if policy.is_mqc and metric.order_count < policy.minimum_orders:
        return "insufficient_orders"

    def exceeds(threshold):
        return metric.value < threshold if policy.operator == "lt" else metric.value >= threshold

    if policy.is_mqc and exceeds(policy.suspension):
        return "suspension_threshold"
    if exceeds(policy.alarm):
        return "alarm" if policy.is_mqc else "below_reference"
    return "ok"
