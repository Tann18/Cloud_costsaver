import random

def get_cpu_usage():
    cpu = random.randint(1, 100)

    # occasional spike
    if random.random() < 0.1:
        cpu = random.randint(80, 100)

    return cpu