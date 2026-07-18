# 1. We tell Python to open the 'server.log' file in Read ('r') mode
# 'with' ensures Python safely closes the file when we are done
with open("backend/server.log", "r") as file:
    # 2. We loop through the physical file line-by-line
    for line in file:
        # We use .strip() to remove extra spacing at the end of each line
        clean_line = line.strip()
        
        # 3. If a line contains a critical error, we print it
        if "[CRITICAL]" in clean_line:
            print(f"🚨 FOUND CRITICAL ERROR IN FILE: {clean_line}")