from genworlds.agents.base_agent.thoughts.single_eval_thought_generator import SingleEvalThoughtGenerator
from genworlds.agents.base_agent.prompts.navigation_generator_prompt import NavigationGeneratorPrompt


class NavigationThought(SingleEvalThoughtGenerator):

    def __init__(
        self,
        openai_api_key: str,
        name: str,
        role: str,
        background: str,
        personality: str,
        topic_of_conversation: str,
        constraints: list[str],
        evaluation_principles: list[str],
        n_of_thoughts: int,
    ):

        navigation_output_parameter_generator = lambda llm_params: {
            "inventory": {
                "type": "array",
                "description": "list the ids of the items in your inventory",
                "items": {
                    "type": "string",
                },
            }, 
            "step_completed": {
                "type": "string",
                "description": "If you completed a step of your plan, put it here, as well as an explanation of how you did it",
            }, 
            "plan": {
                "type": "array",
                "description": "A numbered list of an updated plan", 
                "items": {
                    "type": "string",
                },
            },
            "next_action_aim": {
                "type": "string",
                "description": "What is the aim of the next action you want to take?",
            },
            "next_action": {
                "type": "string",
                "enum": list(llm_params['relevant_commands'].keys()),
                "description": "What is the next action you want to take? Example: \"EntityClass:action_type_1\"",
            }, 
            "violated_constraints": {
                "type": "array",
                "description": """
List any constraints form the section "## Constraints" that this action would violate.
""",
                "items": {
                    "type": "string",
                },
            },
            "is_action_valid": {
                "type": "string",
                "description": """
Assess whether the selected next action is valid based on the current state of the world. 
Example: "Yes, opening the door is valid because I have the key to the door in my inventory"
    """, 
            },
        }
        
        super().__init__(
            openai_api_key=openai_api_key,
            prompt_template_class=NavigationGeneratorPrompt,
            llm_params=[
                "plan",
                "goals",
                "memory",
                # "personality_db",
                "agent_world_state",
                "nearby_entities",
                "inventory",
                "relevant_commands",
                "messages",
            ],
            output_parameter_generator=navigation_output_parameter_generator,
            n_of_thoughts=n_of_thoughts,
            generator_role_prompt=
f"""
You are {name}, {role}. You need to come up with the next step to get you closer to your goals. It must be consistent with all of the following information:

## Your background
{background}

## Your personality
{personality}

## Topic of conversation
{topic_of_conversation}
    """,
            generator_results_prompt=
f"""
## Constraints
{constraints}

# Response type
Look at your previous plan, your memories about what you have done recently and your goals, and propose {{num_thoughts}} possible plans that advance your goals.
Check if you have already completed a step in your plan, and if so, propose the next step as the first one.
Then, select the next action that you want to do to achieve the first step of your plan.
Check that the action is in the list of available actions, and that you meet all the preconditions for the action.
If you do not have a plan, propose a new plan.
""",
            evaluator_role_prompt=f"You are {name}, {role}. You are trying to evaluate a number of actions to see which will get you closer to your goals. It must be consistent with the following information:",
            evaluator_results_prompt=
f"""
## Choose the best action
In a previous step, you have generated some possible plans. Now, you need to evaluate them and choose the best one.

## Evaluation principles
{evaluation_principles}

## Constraints
- Check that the proposed action is in the list of available actions
- That you meet all the preconditions for the action, like having the correct items in your inventory
{constraints}

# Response type
Return the best plan of the following options:
{{thought_to_evaluate}}
""",
            verbose=True,
            model_name="gpt-4",
        )