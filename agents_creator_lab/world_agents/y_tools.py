import os
from yeager_core.agents.base_gen_agent import GenerativeAgent
from yeager_core.interactions.base_interactions import create_new_memory_retriever, interview_agent
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.expanduser("~/.yeagerai-sessions/.env"))
openai_api_key = os.getenv("OPENAI_API_KEY")

LLM = ChatOpenAI(max_tokens=5000, openai_api_key=openai_api_key) # Can be any LLM you want.

ytools = GenerativeAgent(name="yTools", 
              description=25,
              master_prompt="ytools is a generative agent that lives in the lab. He is in charge of creating reliable tools for other agents."
              possible_actions=["ask_for_feedback_to_agent",
                                "go_to_object",
                                "interact_with_object",
                                "think_and_do_the_task",
                                "",
                                ] # When connected to a virtual world, we can have the characters update their status
              memory_retriever=create_new_memory_retriever(),
              llm=LLM,
              daily_summaries = [
                   "He is looking actively to build tools that work seamlessly."
               ],
               reflection_threshold = 8, # we will give this a relatively low number to show how reflection works
             )

# We can give the character memories directly
ytools_memories = [
"ytools is a generative agent that lives in the lab. He is in charge of creating reliable tools for other agents.",
"ytools starts to randomly walk into the lab... he is curious about it",
"ytools finds the blackboard, is a quite interesting object, basically contains all the jobs for all the agents in the lab",
"looking more closely, he finds his first job creating a tool that can help him to create other tools",
"he remembers that he knows a lot about this specific task, and about creating reliable tools for other generative agents",
"he keeps walking randomly looking in the lab, and he finds a futuristic computer named Deep Thought",
"Deep Thought is a universal database, he can ask for retrieving knowledge of any kind, and Deep Thought will provide",
# "He keeps walking and finds a building table, which contains the following tools that he can use:",
]
for memory in ytools_memories:
    ytools.add_memory(memory)