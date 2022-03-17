import platform

def on_arm_machine():
    return "arm" in platform.machine()