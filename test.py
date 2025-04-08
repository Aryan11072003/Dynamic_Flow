import requests
url="http://localhost:5000/chat"

chat_history_1=[
    {"role": "assistant", "content": '{"bot_reply": "Hello! I\'m excited to help you find the perfect property in India.", "followupMessage": "Which city are you interested in?", "Options": ["Mumbai", "Bangalore", "Gurgaon", "Hyderabad"]}'},
        {"role": "user", "content": "Gurgoan"},
        {"role": "assistant", "content": '{"bot_reply": "Gurgaon is a fantastic choice with so many vibrant neighborhoods to explore!", "followupMessage": "What type of property are you interested in?", "Options": ["Apartment", "Villa", "Independent House", "Plot of Land"]}'},
        {"role": "user", "content": "Appartment"},
        {"role": "assistant", "content": '{"bot_reply": "Great choice! Apartments offer convenience and modern living.", "followupMessage": "What is your preferred budget range for the apartment?", "Options": ["Under ₹50 Lakhs", "₹50 Lakhs - ₹1 Crore", "₹1 Crore - ₹2 Crores", "Above ₹2 Crores"]}'},
        {"role": "user", "content": "1 crores"},
        {"role": "assistant", "content": '{"bot_reply": "Excellent! That\'s a popular budget range with plenty of options available.", "followupMessage": "What size of apartment are you looking for?", "Options": ["1 BHK", "2 BHK", "3 BHK", "4 BHK"]}'},
        {"role": "user", "content": "3bhk"},
        {"role": "assistant", "content": "Great choice! Having a gym and swimming pool in the complex is fantastic for a healthy lifestyle.  Follow-Up Question: What is your preferred location within Gurgaon for the apartment?  Options:  Sohna Road  Golf Course Road  MG Road  Cyber City"},
        {"role": "user", "content": "sohna road"},
        {"role": "assistant", "content": "Sohna Road is a prime location with excellent connectivity and amenities! Would you like to see property options now, or continue refining your search?  Options:  See property options now  Refine search further  Add more preferences  Start over"},
        {"role": "user", "content": "show me property now"}
    
]

chat_history_2=[
     {"role": "assistant", "content": "Hello! I'm excited to help you find the perfect property in India. Follow-Up Question: Which city are you interested in? Options: Mumbai Bangalore Gurgaon Hyderabad"},
    {"role": "user", "content": "Mumbai"},
    {"role": "assistant", "content": "Mumbai is a fantastic choice with so many vibrant neighborhoods to explore! Follow-Up Question: What type of property are you interested in? Options: Apartment Villa Independent House Plot of Land"},
    {"role": "user", "content": "Apartment"},
    {"role": "assistant", "content": "Great choice! Apartments offer convenience and modern living. Follow-Up Question: What is your preferred budget range for the apartment? Options: Under ₹50 Lakhs ₹50 Lakhs - ₹1 Crore ₹1 Crore - ₹2 Crores Above ₹2 Crores"},
    {"role": "user", "content": "1 Crore"},
    {"role": "assistant", "content": "Excellent! That's a popular budget range with plenty of options available. Follow-Up Question: What size of apartment are you looking for? Options: 1 BHK 2 BHK 3 BHK 4 BHK"},
    {"role": "user", "content": "3 BHK"},
    {"role": "assistant", "content": "Great choice! Having a gym and swimming pool in the complex is fantastic for a healthy lifestyle. Follow-Up Question: What is your preferred location within Mumbai for the apartment? Options: Bandra Andheri Powai South Mumbai"},
    {"role": "user", "content": "Andheri"},
    {"role": "assistant", "content": "Andheri is a prime location with excellent connectivity and amenities! Would you like to see property options now, or continue refining your search? Options: See property options now Refine search further Add more preferences Start over"},
    {"role": "user", "content": "Show me property now"}
]

chat_history_3=[
    {"role": "assistant", "content": '{"bot_reply": "Hello! I\'m excited to help you find the perfect property in India.", "followupMessage": "Which city are you interested in?", "Options": ["Mumbai", "Bangalore", "Gurgaon", "Hyderabad"]}'},
        {"role": "user", "content": "Gurgoan"},
        {"role": "assistant", "content": '{"bot_reply": "Gurgaon is a fantastic choice with so many vibrant neighborhoods to explore!", "followupMessage": "What type of property are you interested in?", "Options": ["Apartment", "Villa", "Independent House", "Plot of Land"]}'},
        {"role": "user", "content": "Appartment"},
        {"role": "assistant", "content": '{"bot_reply": "Great choice! Apartments offer convenience and modern living.", "followupMessage": "What is your preferred budget range for the apartment?", "Options": ["Under ₹50 Lakhs", "₹50 Lakhs - ₹1 Crore", "₹1 Crore - ₹2 Crores", "Above ₹2 Crores"]}'},
        {"role": "user", "content": "1 crores"},
        {"role": "assistant", "content": '{"bot_reply": "Excellent! That\'s a popular budget range with plenty of options available.", "followupMessage": "What size of apartment are you looking for?", "Options": ["1 BHK", "2 BHK", "3 BHK", "4 BHK"]}'},
        {"role": "user", "content": "3bhk"},
        {"role": "assistant", "content": "Great choice! Having a gym and swimming pool in the complex is fantastic for a healthy lifestyle.  Follow-Up Question: What is your preferred location within Gurgaon for the apartment?  Options:  Sohna Road  Golf Course Road  MG Road  Cyber City"},
        {"role": "user", "content": "sohna road"},
]


response = requests.post(url, json={"chat_history": chat_history_1}, verify=False)
# response = requests.post(url, json={"chat_history": chat_history_2}, verify=False)
# response = requests.post(url, json={"chat_history": chat_history_3}, verify=False)

print("Status Code:", response.status_code)
print("Response:", response.json())