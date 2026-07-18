# 1. We define a log message variable
log_line = "2026-07-14 [CRITICAL] Database went offline!"

# 2. We ask Python to check if "[CRITICAL]" is in our log line
if "[CRITICAL]" in log_line:
    # This runs ONLY if the condition is True
    print("🚨 ALERT: An urgent critical error was found!")
else:
    # This runs ONLY if the condition is False
    print("✅ System is running normally.")
    