# agent.py

import os
from dotenv import load_dotenv

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import LLMChain 

# Import the custom tool we built earlier
from sales_brief import generate_sales_brief

#import from voice_generator
from voice_generator import text_to_speech_bytes

# Load your .env vault
load_dotenv()

def start_sales_agent(target_url):
    print(f"\n[1/3] Fetching data from {target_url}...")
    
    # 1. Generate the brief using your existing tool
    brief = generate_sales_brief(target_url)
    
    if "Error" in brief:
        print("Failed to generate brief. Exiting.")
        return

    print("[2/3] Brief generated! Injecting into the agent's brain...")

    # 2. Initialize the Groq LLM (using the fast Llama 3.1 model)
    llm = ChatGroq(
        temperature=0.7, # 0.7 gives it a conversational, creative tone
        model_name="llama-3.1-8b-instant" 
    )

    # 3. Create the System Prompt and Memory Placeholder
    # This is where we strictly define who the agent is and who it is talking to.
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are an elite, highly persuasive B2B sales development representative. "
         "You are cold-calling a prospect from the following company. Here is their profile:\n\n"
         f"{brief}\n\n"
         "Your goal is to pitch our 'AI Automation Services' as the perfect solution to their specific bottlenecks. "
         "Keep your responses short, punchy, and conversational (1-3 sentences max). Do not sound like a robot."
        ),
        # This acts as the "Memory Buffer" slot
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_input}")
    ])

    # 4. Set up the Conversation Memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # 5. Build the Chain (Connects the LLM, Prompt, and Memory)
    conversation_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )

    print("[3/3] Agent Ready.")
    print("\n==================================================")
    print("CALL CONNECTED: The AI Agent is ready to pitch you.")
    print("   (Type 'exit' or 'quit' to hang up)")
    print("==================================================\n")

    # 6. The Chat Loop
    # We will pretend the user answers the phone with a simple "Hello?" to start the pitch
    initial_input = "Hello?"
    response = conversation_chain.predict(user_input=initial_input)
    print(f"🤖 AGENT: {response}\n")
    text_to_speech_bytes(response)

    while True:
        # Get your reply
        user_msg = input("You (as the prospect): ")
        
        # Check if you want to end the chat
        if user_msg.lower() in ['exit', 'quit']:
            print("\n📞 Call ended.")
            break

        # Pass your reply to the agent
        response = conversation_chain.predict(user_input=user_msg)
        print(f"\n🤖 AGENT: {response}\n")
        text_to_speech_bytes(response)

if __name__ == "__main__":
    # You can change this URL to test the agent against different companies
    target_company = "https://stripe.com" 
    start_sales_agent(target_company)