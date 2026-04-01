# 不只是存数据，还要处理数据
def process_health_data(data):
    bmi = calculate_bmi(data.weight, data.height)
    risk_level = evaluate_risk(bmi, data.age)
    return bmi, risk_level