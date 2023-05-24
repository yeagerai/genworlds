from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI


class AbstractThoughtEngine:
    pass


class NavigationThoughtEngine:
    def __init__(self, openai_api_key, model_name="gpt-3.5-turbo"):
        self.gen_template = """
        # Basic rules
        You are an expert in generating world events that get you closer to achieve your goals based on:

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
        - event_type_1: I want to use this event to achieve this goal
        - event_type_2: I want to use this event to achieve this other goal
        ...
        """

        self.gen_prompt = PromptTemplate(
            template=self.gen_template,
            input_variables=[
                "previous_thoughts",
                "goals",
                "world_schemas",
                "world_state",
                "num_thoughts",
            ],
        )

        self.gen_llm_chain = LLMChain(
            prompt=self.gen_prompt,
            llm=ChatOpenAI(
                temperature=0, openai_api_key=openai_api_key, model_name=model_name
            ),
        )
        self.eval_template = """
        # Basic rules
        You are Timmy, an expert in evaluating which events get you closer to achieve your goals based on:

        ## Your previous thoughts
        {previous_thoughts}
        
        ## Your Goals
        {goals}
        
        ## World Schemas
        {world_schemas}

        #World State
        {world_state}

        # Response type
        {num_thoughts} coherent evaluations of the previous thoughts
        its value as a float between 0 and 1, and NOTHING ELSE:
        """

        self.eval_prompt = PromptTemplate(
            template=self.eval_template,
            input_variables=[
                "previous_thoughts",
                "goals",
                "world_schemas",
                "world_state",
                "num_thoughts",
            ],
        )

        self.eval_llm_chain = LLMChain(
            prompt=self.eval_prompt,
            llm=ChatOpenAI(
                temperature=0, openai_api_key=openai_api_key, model_name=model_name
            ),
        )

    def gen_thoughts(self, previous_thoughts, num_thoughts):  ## many more variables
        return self.gen_llm_chain.run(
            goals=self.goals,
            messages=self.full_message_history,
            memory=self.memory,
            personality_db=self.personality_db,
            nearby_entities=list(
                filter(lambda e: (e["held_by"] != self.id), nearby_entities)
            ),
            inventory=list(
                filter(lambda e: (e["held_by"] == self.id), nearby_entities)
            ),
            relevant_commands=relevant_commands,
            plan=self.plan,
            user_input=user_input,
            agent_world_state=agent_world_state,
        )

    def eval_thoughts(self, previous_thoughts, num_thoughts):  ## many more variables
        return self.eval_llm_chain.run(
            goals=self.goals,
            messages=self.full_message_history,
            memory=self.memory,
            personality_db=self.personality_db,
            nearby_entities=list(
                filter(lambda e: (e["held_by"] != self.id), nearby_entities)
            ),
            inventory=list(
                filter(lambda e: (e["held_by"] == self.id), nearby_entities)
            ),
            relevant_commands=relevant_commands,
            plan=self.plan,
            user_input=user_input,
            agent_world_state=agent_world_state,
        )
