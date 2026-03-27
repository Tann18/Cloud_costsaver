def auto_fix(cpu):
    if cpu < 5:
        return "Stopped idle instance"
    elif cpu > 90:
        return "Scaled down high usage"
    return "No action needed"