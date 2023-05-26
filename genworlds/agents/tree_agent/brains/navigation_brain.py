from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI

from genworlds.agents.tree_agent.tree_of_thoughts import TreeOfThoughts


class NavigationBrain:
    def __init__(
        self, openai_api_key, model_name="gpt-3.5-turbo", search_algorithm="BFS"
    ):
        self.search_algorithm = search_algorithm
        self.tot = TreeOfThoughts(
            self.gen_thoughts, self.eval_thoughts, self.search_algorithm
        )

        self.gen_template = """
        # Basic rules
        You are {ai_name}, an expert in generating world events that get you closer to achieve your goals based on:

        ## Your Goals
        {goals}

        ## Your Plan
        {plan}

        ## Your previous thoughts if any
        {previous_thoughts}
        
        ## Recent Memories 
        {memory}

        ##World State
        {agent_world_state}

        ## Nearby Entities
        {nearby_entities}

        ## Inventory
        {inventory}

        ## Events that you can use to achieve your goals
        {relevant_commands}


        # Response type
        A bullet list containing {num_thoughts} coherent events that can be your next thought, each one with the following format:
        - event_type_1: I want to use this event to achieve this goal
        - event_type_2: I want to use this event to achieve this other goal
        ...

        A bullet list with the following steps of your plan:
        - step 1: I want to use this event to achieve this goal
        - step 2: I want to use this event to achieve this other goal
        ...
        """

        self.gen_prompt = PromptTemplate(
            template=self.gen_template,
            input_variables=[
                "ai_name",
                "num_thoughts",  # fixed int
                "previous_thoughts",  # iterative
                "plan",  # iterative
                "goals",  # fixed by the user list
                "memory",  # this is no good, we have to improve it before sending it to the AI, a summary of everything in one paragraph
                "agent_world_state",  # listening_antena input
                "nearby_entities",  # name description and location
                "inventory",  # name description
                "relevant_commands",  # just the event types, and the description of what the event does (not even the name)
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
        You are {ai_name}, an expert in evaluating which events get you closer to achieve your goals based on:

        ## Your Goals
        {goals}

        ## Your Plan
        {plan}

        ## Your previous thoughts if any
        {previous_thoughts}
        
        ## Recent Memories 
        {memory}

        ##World State
        {agent_world_state}

        ## Nearby Entities
        {nearby_entities}

        ## Inventory
        {inventory}

        ## Events that you can use to achieve your goals
        {relevant_commands}

        # Response type
        {num_thoughts} coherent evaluations of the previous thoughts
        its value as a float between 0 and 1, and NOTHING ELSE:
        """

        self.eval_prompt = PromptTemplate(
            template=self.eval_template,
            input_variables=[
                "ai_name",
                "num_thoughts",  # fixed int
                "previous_thoughts",  # iterative
                "plan",  # iterative
                "goals",  # fixed by the user list
                "memory",  # this is no good, we have to improve it before sending it to the AI, a summary of everything in one paragraph
                "agent_world_state",  # listening_antena input
                "nearby_entities",  # name description and location
                "inventory",  # name description
                "relevant_commands",  # just the event types, and the description of what the event does (not even the name)
            ],
        )

        self.eval_llm_chain = LLMChain(
            prompt=self.eval_prompt,
            llm=ChatOpenAI(
                temperature=0, openai_api_key=openai_api_key, model_name=model_name
            ),
        )

    def gen_thoughts(
        self,
        ai_name,
        num_thoughts,
        previous_thoughts,
        plan,
        goals,
        memory,
        agent_world_state,
        nearby_entities,
        inventory,
        relevant_commands,
    ):
        # prepare the input variables
        return self.gen_llm_chain.run(
            ai_name=ai_name,
            num_thoughts=num_thoughts,
            previous_thoughts=previous_thoughts,
            plan=plan,
            goals=goals,
            memory=memory,
            agent_world_state=agent_world_state,
            nearby_entities=nearby_entities,
            inventory=inventory,
            relevant_commands=relevant_commands,
        )

    def eval_thoughts(
        self,
        ai_name,
        num_thoughts,
        previous_thoughts,
        plan,
        goals,
        memory,
        agent_world_state,
        nearby_entities,
        inventory,
        relevant_commands,
    ):
        # prepare the input variables
        return self.eval_llm_chain.run(
            ai_name=ai_name,
            num_thoughts=num_thoughts,
            previous_thoughts=previous_thoughts,
            plan=plan,
            goals=goals,
            memory=memory,
            agent_world_state=agent_world_state,
            nearby_entities=nearby_entities,
            inventory=inventory,
            relevant_commands=relevant_commands,
        )

    def run(self):
        final_response = self.tot.solve(  # kwargs
            initial_state,
            thought_limit,
            max_depth,
            breadth,
            value_threshold,
            ai_name=ai_name,
            num_thoughts=num_thoughts,
            previous_thoughts=previous_thoughts,
            plan=plan,
            goals=goals,
            memory=memory,
            agent_world_state=agent_world_state,
            nearby_entities=nearby_entities,
            inventory=inventory,
            relevant_commands=relevant_commands,
        )
        # parse the thought and convert it into an event schema
        # return just the event type that is in the thought
        pass
