from genworlds.agents.base_agent.brains.single_eval_brain import SingleEvalBrain
from genworlds.agents.base_agent.prompts.execution_generator_prompt import ExecutionGeneratorPrompt


class EventFillerBrain(SingleEvalBrain):

    def __init__(
        self,
        openai_api_key: str,
        name: str,
        role: str,
        background: str,
        topic_of_conversation: str,
        constraints: list[str],
        evaluation_principles: list[str],
        n_of_thoughts: int,
    ):

        event_filler_output_parameter_generator = lambda llm_params: llm_params['command_to_execute']['args']

        super().__init__(
            openai_api_key=openai_api_key,
            prompt_template_class=ExecutionGeneratorPrompt,
            llm_params=[
                "plan",
                "goals",
                "memory",
                "personality_db",
                "agent_world_state",
                "nearby_entities",
                "inventory",
                "command_to_execute",
                "previous_brain_outputs",
            ],
            output_parameter_generator=event_filler_output_parameter_generator,
            n_of_thoughts=n_of_thoughts,
            generator_role_prompt=
f"""You are {name}, {role}. In previous steps, you have selected an action to execute, and possibly generated some of the response parameters - make sure to include those exactly. 
You now need to generate a valid set of JSON parameters for the command to execute, based on the following information:

## Your background
{background}

## The topic of conversation
{topic_of_conversation}
""",
            generator_results_prompt=
f"""
# Response type
Generate exactly {{num_thoughts}} possible options for completing the arguments of the command to execute

## Constraints
{constraints}
""",
            evaluator_role_prompt=f"You are {name}, {role}. ou need to evaluate the provided set of JSON parameters based on their correctness, with respect to all of the following information:",
            evaluator_results_prompt=
f"""
## Parameters to evaluate
Evaluate the following list of possible parameter sets in terms of their correctness:
{{thought_to_evaluate}}

## Evaluation principles
{evaluation_principles}

## Constraints
- target_id must be the ID of the entity that provides the action
{constraints}

# Response type
Return the best parameter set      
""",
            verbose=True,
            model_name="gpt-4-0613",
        )