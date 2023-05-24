from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI

class AbstractThoughtEngine:
    pass

class PodcastThoughtEngine:
    def __init__(self, openai_api_key, model_name="gpt-3.5-turbo"):
        self.gen_template = """
        # Basic rules
        You are Timmy, an expert in generating world events that get you closer to achieve your goals based on:

        ## Your previous thoughts
        {previous_thoughts}
        
        ## Your Goals
        {goals}
        
        ## World Schemas
        {world_schemas}

        #World State
        {world_state}

        # Response type
        A json file containing {num_thoughts} coherent events to continue the navigation process:
        {{{{{{{{{{json structure to be defined}}}}}}}}}}
        """

        self.gen_prompt = PromptTemplate(
            template=self.gen_template,
            input_variables=[
                "previous_thoughts", 
                "goals", 
                "world_schemas",
                "world_state",
                "num_thoughts",
            ]
        )
        
        self.gen_llm_chain = LLMChain(
            prompt=self.gen_prompt, 
            llm=ChatOpenAI(
                temperature=0, 
                openai_api_key=openai_api_key, 
                model_name=model_name
            )
        )
        self.eval_template = """
        # Basic rules
        You are Timmy, an expert in evaluating which events get you closer to achieve your goals based on:

        ## Your previous thoughts
        {state_text}
        
        ## Your Goals
        {goals}
        
        ## World Schemas
        {world_schemas}

        #World State
        {world_state}

        # Response type
        {n_thoughts} coherent evaluations of the previous thoughts
        its value as a float between 0 and 1, and NOTHING ELSE:
        """

        self.eval_prompt = PromptTemplate(
            template=self.eval_template,
            input_variables=[
                "state_text", 
                "goals", 
                "world_schemas",
                "world_state",
                "n_thoughts",
            ]
        )
        
        self.eval_llm_chain = LLMChain(
            prompt=self.eval_prompt, 
            llm=ChatOpenAI(
                temperature=0, 
                openai_api_key=openai_api_key, 
                model_name=model_name
            )
        )
    
    def gen_thoughts(self, previous_thoughts, num_thoughts):
        return self.gen_llm_chain.run()

    def eval_thoughts(self, previous_thoughts, num_thoughts):
        return self.eval_llm_chain.run()