import dspy
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, List

load_dotenv()

def set_dspy():
    lm = dspy.OpenAI(model='gpt-4-0613')
    dspy.configure(lm=lm)

from pydantic import BaseModel, Field
from typing import Literal, List

class Response(BaseModel):
    # This is a response. should contain users for which paper is interesting, and reasoning?
    users: List[str] = Field(..., description="The users for which this paper might be interesting.")

class Sig(dspy.Signature):

    paper_abstract: str = dspy.InputField(desc="The abstract of a paper. Your task is to tell for which users this paper might be interesting.")
    user_context: list = dspy.InputField(desc="Descriptions of the users. Use this information to know for which users the paper might be interesting.")

    users: Response = dspy.OutputField(desc="The users for which this paper might be interesting.")

class Recommender(dspy.Module):
    def __init__(self):
        self.recommender = dspy.TypedChainOfThought(Sig)

    def forward(self, paper_abstract: str, user_context: list):
        return self.recommender(
            paper_abstract=paper_abstract,
            user_context=user_context
        )


class PQA(dspy.Module):
    def __init__(self):
        self.qa = dspy.Predict('context, question -> answer')

    def forward(self, context: str, question: str):
        return self.qa(
            context=context,
            question=question
        )


if __name__ == "__main__":
    set_dspy()
    recommender = Recommender()
    pqa = PQA()

    r = pqa(
        context="This is a context.",
        question="What is the answer?"
    )

    print(r)
