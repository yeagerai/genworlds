from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI


class MemorySummarizer:
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.summary_template = """
        This is what happened:
        {memory}
        Summarize what happened in one line. Every event should have the following structure:
        AgentName did Action which implies X. 
        If there is nothing new to summarize, say "NOTHING_NEW"
        """

        self.summary_prompt = PromptTemplate(
            template=self.summary_template,
            input_variables=[
                "memory",
            ],
        )

        self.chat = ChatOpenAI(
            temperature=0, model_name=model_name, openai_api_key=openai_api_key
        )
        self.chain = LLMChain(llm=self.chat, prompt=self.summary_prompt)

    def summarize(
        self,
        memory: str,
    ) -> str:
        """
        Summarize the memory in one line.
        """
        return self.chain.run(memory=memory)
