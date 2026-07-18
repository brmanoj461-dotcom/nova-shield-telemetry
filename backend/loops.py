# 1. We store MULTIPLE log lines in one single List variable
log_list = [
    "2026-07-14 [INFO] User logged in",
    "2026-07-14 [CRITICAL] Database crashed!",
    "2026-07-14 [INFO] Page loaded in 0.5s",
    "2026-07-14 [CRITICAL] Memory limit reached!"
]

# 2. We use a For Loop to inspect each line one-by-one
for line in log_list:
    # Python will run this block of code for every line in our list!
    if "[CRITICAL]" in line:
        print(f"🚨 ALERT: Found critical issue -> {line}")