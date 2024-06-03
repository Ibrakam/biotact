data_for_option1 = {"action": "Reject", "user_id": 12}

data_for_option2 = {"action": "Accept", "user_id": 12}

print([data_for_option1, data_for_option2])
for i in [{"action": "Reject", "user_id": 12}, {"action": "Accept", "user_id": 12}]:
    print(i["action"], i["user_id"])