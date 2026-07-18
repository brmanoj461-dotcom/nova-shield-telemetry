# 1. We create an empty List to act as our temporary "Database Table"
alert_database = []

# 2. Open and read the server log file
with open("backend/server.log", "r") as file:
    for line in file:
        clean_line = line.strip()
        
        if "[CRITICAL]" in clean_line:
            parts = clean_line.split(" | ")
            tenant = parts[0]
            timestamp = parts[1]
            error_msg = parts[2]
            
            # 3. We bundle the details into a structured "Record" (Dictionary)
            alert_record = {
                "tenant": tenant,
                "time": timestamp,
                "issue": error_msg
            }
            
            # 4. We save this record into our "Database" list!
            alert_database.append(alert_record)

# 5. Let's simulate what a UI would do: Print out the saved history!
print("--- 🗄️ RETRIEVING SAVED ALERTS FROM DATABASE ---")
for record in alert_database:
    print(f"Stored Alert -> Customer: {record['tenant']} | Time: {record['time']} | Issue: {record['issue']}")
print("-----------------------------------------------")