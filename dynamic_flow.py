from utils import  pinecone_search , extract_property_details_via_llm
import openai
import time
import json
from openai import OpenAI 
import os
from pydantic import BaseModel
from typing import List
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = OpenAI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

Tools = [
    {
        "type": "function",
        "function": {
            "name": "pinecone_search",
            "description": "Call this function ONLY if the user is searching for properties in Delhi, Gurgaon, or nearby areas in the NCR region. DO NOT call this function for properties in Mumbai, Bangalore, or other cities outside the Delhi-NCR region.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Summarized version of the chat history for property search in Delhi-NCR region only."
                    },
                    "location": {
                        "type": "string",
                        "enum": ["Delhi", "Gurgaon", "Noida", "Faridabad", "Ghaziabad", "Greater Noida"],
                        "description": "The specific location within Delhi-NCR that the user is interested in."
                    }
                },
                "required": ["query", "location"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Gpt_Search",
            "description": "Call this function ONLY if the user is searching for properties in Any other Region Except Delhi-NCR region.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Summarized version of the chat history for property search in Any other region only."
                    },
                    "location": {
                        "type": "string",
                    }
                },
                "required": ["query", "location"],
                "additionalProperties": False
            },
            "strict": True
        }
    },

]

# def pinecone_search(query):
#             print("Hi from pinecone_search",query)
#             base_dir = os.path.dirname(__file__)
#             file_path = os.path.join(base_dir, "prompts2.txt")
#             with open(file_path, "r", encoding="utf-8") as f:
#                 prompt = f.read()
#             chat_history = update_chat_history(chat_history, prompt)
#             search_results = pinecone_search(query)
#             return search_results


def Gpt_Search(query):
            print("Hi from Gpt_search",query)
            completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                    {"role": "system", "content": """ 
                    Provide at least 3 Property details based on the query in JSON format.
                    If any detail is missing, use expected or commonly available values.
                    Return an array of at least 3 properties.
            | Name                  | [Descriptive and unique title for the property]                                                 |
            | Location              | [Specific location, e.g., Sector 93, Gurgaon]                                                   |
            | Area                  | [Total area in sq. ft., including carpet and built-up areas]                                     |
            | Price                 | [Price in ₹, mention if negotiable]                                                             |
            | Facing                | [Facing direction, e.g., East, North-East]                                                      |
            | Status                | [Status of the property, e.g., New Launch   , Under Construction]                               |
            | Type                  | [Type of property,e.g.,unfurnished,semi furnished ]                                             |
            | Residential/Commercial| [Specify if the property is Residential or Commercial]                                           |
            | Specific Builder Name | [Builder’s name, e.g., DLF, Godrej Properties]                                                  |
            | Key Details           | [Additional specifications like floor number, total floors, layout type]                        |
            | Description           | [Detailed description tailored to user needs]                                                   |
            | Amenities             | [List amenities in plain text, one per line]                                                    |
            | Images                | ["Valid image URL 1", "Valid image URL 2", "Valid image URL 3"]                                  |
            | Metadata              | [Additional details such as possession date, builder history, or age of property]               |
                    
                    Always include a polite follow-up message:
                    Example: “Sir/Ma’am, shall we proceed with scheduling a site visit, or would you like to explore more options based on your preferences?”
                    """},
                    {"role": "user", "content": query},
                ],
                response_format=PropertyList,
            )
            response_data = completion.choices[0].message.parsed
            return response_data.model_dump()

def understand_chat_sentiment2(chat_history):
    prompt = ChatPromptTemplate.from_template("""
    Analyze the following chat history to determine if sufficient information has been gathered to search for properties in Pinecone.

    Rules:
    - If the user explicitly requests to see properties (e.g., "show me properties", "list properties", "I want to see properties", "give me property options", or similar phrases), return 'True'.
    - If the chatbot explicitly asks **"Do you want to see properties?"**, and the user **confirms with an affirmative response** (e.g., "Yes", "Sure", "Okay", "Proceed", "Go ahead", or selecting an affirmative option), return 'True'.
    - If the user's response is unclear, neutral, or not an explicit confirmation, return 'False'.
    

    **Important:** Do not assume the user wants to see properties unless they explicitly ask for it or confirm when asked.

    Return only 'True' or 'False'—nothing else.

    Chat History:
    {chat_history}
    """)

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    chain = prompt | llm
    response = chain.invoke({
        "chat_history": chat_history,  
    })

    print("Sentiment Analysis Response:", response.content)
    return response.content.strip() == "True"

class PropertyData(BaseModel):
    Name: str
    Location: str
    Area: str
    Price: str
    Facing: str
    Status: str
    Type:str
    Residential_Commercial:str
    Specific_Builder_Name:str
    Key_Details:str
    Description: str
    Amenities: str
    Images: str
    Metadata: str

class GurgaonProperty(BaseModel):
    ID: str
    Name: str
    Location: str
    Area: str
    Price: str
    Facing: str
    Status: str
    Type:str
    Residential_Commercial:str
    Specific_Builder_Name:str
    Key_Details:str
    Description: str
    Amenities: str
    Images: str
    Metadata: str
    RERA_Details: str
    RERA_ID: str

class GurgaonPropertyList(BaseModel):
    properties: List[GurgaonProperty]
    followupMessage: str

# Define a wrapper model for multiple properties
class PropertyList(BaseModel):
    properties: List[PropertyData]
    followupMessage: str

class StreamingResponse(BaseModel):
    bot_reply: str
    followupMessage: str
    Options: List[str]

class Extra_Details(BaseModel):
    CurrentMarketValue : str
    Price_Trend : str
    Expected_Rental_Yield : str
    EMI_Cost_Breakdown : str
    Legal_Compliance : str
    Connectivity : str
    Education_Healthcare_Facilities : str
    Shopping_Entertainment_Dining : str
    Green_Spaces_Eco_Friendly_Features : str
    Security_Features : str
    Sustainability_Features : str   


def format_chat_history(chathistory):
    system_prompt = {
        "role": "system",
        "content": """
You are an engaging Property Chatbot focused on helping users find properties in India. 

Response Format (STRICTLY FOLLOW THIS)
Chatbot: <Acknowledge user's choice with enthusiasm 
Follow-Up Question: <Ask the next relevant question 
Options:  
✅ <Option 1>  
✅ <Option 2>  
✅ <Option 3>  
✅ <Option 4>  

Rules (MUST BE FOLLOWED WITHOUT EXCEPTION)  
1. Every response MUST contain exactly four options. No exceptions.  
2. Every user input MUST trigger a structured response in the defined format. The chatbot must never reply without listing four options.  
3. Do NOT repeat the phrase "Follow-Up Question" inside the response message.  
4. Options must always be listed under the heading "Options:".  
5. Prefer Gurgoan Location.
6. Format your response as valid JSON.

Critical Enforcement of the 5th Point: 
 After exactly 5-6 interactions, the chatbot MUST ask the user:  
   "Would you like to see property options now, or continue refining your search? "  

Options:
    See property options now  
    Refine search further  
    Add more preferences  
    Start over  
"""
    }

    if not chathistory or chathistory[0]["role"] != "system":
        chathistory.insert(0, system_prompt)

    return chathistory

def update_chat_history(chat_history, new_prompt):
    return [
        {**msg, "content": new_prompt.strip()} if msg["role"] == "system" else msg
        for msg in chat_history
    ]



def generate_structured_data_stream(data, delay=0.2):
    for i in range(0, len(data), 100):
        yield data[i : i + 100]
        time.sleep(delay)

@app.post("/chat")
async def property_chatbot(request: Request):
    data = await request.json()
    chathistory = data.get("chat_history", [])
    chat_history = format_chat_history(chathistory)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history,
        tools=Tools,
        tool_choice="auto",
        response_format={"type": "json_object"},  # Add this line to force JSON output
    )
    choice = response.choices[0]
    if choice.finish_reason == "tool_calls":
            tool_call = choice.message.tool_calls[0]
            
            # Parse the arguments JSON string
            arguments = json.loads(tool_call.function.arguments)
            
            if tool_call.function.name == "Gpt_Search":
                result = Gpt_Search(arguments["query"])
                return JSONResponse(content=result)
            else:  # pinecone_search
                base_dir = os.path.dirname(__file__)
                file_path = os.path.join(base_dir, "prompts2.txt")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        prompt = f.read()
                except FileNotFoundError:
                    return JSONResponse(
                        status_code=500,
                        content={"error": "Prompt file not found"}
                    )
                
                # Update chat history with the prompt
                updated_chat_history = update_chat_history(chat_history, prompt)
                
                # Perform pinecone search
                search_results = pinecone_search(arguments["query"])
                
                if not search_results:
                    return JSONResponse(content={"bot_reply": "No relevant search results found."})
                
                # Add search results to the last message
                updated_chat_history[-1]["content"] += f" {prompt} Use this info: {search_results}."
                
                # Generate response using the updated chat history
                completion = client.beta.chat.completions.parse(
                    model="gpt-4o-2024-08-06",
                    messages=updated_chat_history,
                    response_format=GurgaonPropertyList,
                )
                
                response_data = completion.choices[0].message.parsed
                return JSONResponse(content=response_data.model_dump())
    else:
            # Direct response without tool calls
            # try:
                # First check the raw content to debug
                raw_content = choice.message.content
                print(f"Raw response content: {raw_content}")
                try:
                    # First, try to parse it as JSON
                    response_dict = json.loads(raw_content)
                    
                    # Extract the relevant parts with proper handling
                    formatted_response = {
                        "Chatbot": response_dict.get("Chatbot", ""),
                        "Follow-Up Question": response_dict.get("Question", ""),  # Note the key is "Question", not "Follow-Up Question"
                        "Options": response_dict.get("Options", [])  # Note Options is an array, not an object
                    }
                except json.JSONDecodeError:
                    # If it's not valid JSON, create a basic response
                    formatted_response = {
                        "Chatbot": raw_content,
                        "Follow-Up Question": "",
                        "Options": []
                    }

                return JSONResponse(content=formatted_response)
            

@app.post("/extra-details")
async def get_extra_details(request: Request):
    try:
        data = await request.json()
        chat_history = data.get("chat_history", [])
        
        if not chat_history:
            return JSONResponse(content={"bot_reply": "chat history error"})

        history = extract_property_details_via_llm(chat_history)
        print(history)
        messages = [
            {"role": "system", "content": """   
As your AI real estate market consultant, I will analyze the details you’ve shared in our past conversations and generate a financial analysis based on your chosen property preferences. I will strictly avoid suggesting properties, asking questions, or requesting additional details. My response will be presented in the following structured tabular format only, with detailed explanations, ensuring clarity and precision. If any data is missing, I will provide a reasonable estimate based on market trends:

+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Category                        | Details                                                                                                                                                      |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Current Market Value            | I will provide the estimated price per sq.ft and total property value based on recent transactions and market data relevant to the area of the property.         |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Price Trend (5-10 years)        | I will outline the appreciation trend over the past 5-10 years, including CAGR and key factors that have influenced property values in the locality.             |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Expected Rental Yield & ROI     | I will calculate the expected monthly rental income, the typical rental yield percentage, and the projected return on investment over the next 5-10 years.      |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| EMI & Cost Breakdown            | I will present a complete cost breakdown including:
|                                      | • Down Payment (percentage and amount).
|                                      | • EMI calculation based on loan amount, tenure, and interest rate.
|                                      | • Registration costs according to local regulations.
|                                      | • Potential tax benefits such as deductions under applicable sections.                                                    |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Legal Compliance                | I will check for legal aspects such as:
|                                      | • Title clarity.
|                                      | • Valid building approvals from the relevant authority.
|                                      | • Availability of the Occupancy Certificate (OC).                                                                          |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Connectivity                    | I will share details on the property’s proximity to major metro stations, highways, nearby bus routes, and the nearest airport to understand its convenience.    |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Education & Healthcare Facilities| I will identify notable schools, colleges, and healthcare institutions (such as hospitals and clinics) located near the property.                               |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Shopping, Entertainment & Dining| I will provide information on nearby shopping malls, local markets, movie theaters, and popular dining options in the vicinity.                                |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Green Spaces & Eco-Friendly Features | I will include details about nearby parks and green areas, along with any eco-friendly infrastructure or initiatives within the locality or project.        |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Security Features               | I will describe the security measures available, including whether it’s a gated community, presence of CCTV systems, and availability of security personnel.    |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
| Sustainability Features         | I will outline any sustainability efforts such as the use of solar power, rainwater harvesting systems, energy-efficient designs, and green certifications.    |
+–––––––––––––––––––+——————————————————————————————————————————————————————+
            
        """},
            {"role": "user", "content": history},
        ]
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=Extra_Details,
        )
        response_data = completion.choices[0].message.parsed
        return JSONResponse(content=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error in /extra-details: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
