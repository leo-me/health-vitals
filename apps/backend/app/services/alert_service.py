# 不只是存 alert，还要决定"要不要触发"
def check_alert_rules(health_data):
    if health_data.heart_rate > 120:
        trigger_alert(user_id, "heart rate too high")