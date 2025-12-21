from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)


class SmartAPILLM:
#llm engine
    def __init__(self):
        # init HuggingFace inference 
        self._hf_endpoint = HuggingFaceEndpoint(
            repo_id="deepseek-ai/DeepSeek-V3.2",
            task="text-generation"
        )

        self.llm = ChatHuggingFace(llm=self._hf_endpoint)

        # system instruction 
        self.system_message = SystemMessage(
            content=(
                "You are an expert software assistant.\n"
                "You MUST answer strictly using the provided documentation.\n"
                "Do NOT invent endpoints, parameters, or responses.\n"
                "If information is missing, clearly state it."
            )
        )

        # prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "query"],
            template=(
                "DOCUMENTATION:\n"
                "{context}\n\n"
                "USER QUERY:\n"
                "{query}\n\n"
                "INSTRUCTIONS:\n"
                "- Use ONLY the documentation above\n"
                "- When code is requested, return executable code in the language used in the documentation\n"
                "- Enclose code in triple backticks ```\n"
                "- Do not hallucinate or guess\n"
            )
        )

    def generate_answer(self, context: str, query: str) -> str:
        #generate a response
        prompt = self.prompt_template.format(
            context=context,
            query=query
        )

        messages = [
            self.system_message,
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)

        return response.content
