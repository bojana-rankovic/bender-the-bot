import dspy
from dotenv import load_dotenv

load_dotenv()


def set_dspy():
    lm = dspy.OpenAI()
    dspy.configure(lm=lm)

from pydantic import BaseModel

all_users = (
    "andres",
    "bojana",
    "victor"
)

from typing import Literal, List

class User(BaseModel):
    name: str#Literal[*all_users]

class Response(BaseModel):
    # This is a response. should contain users for which paper is interesting, and reasoning?
    users: List[User]

class Sig(dspy.Signature):

    paper_abstract: str = dspy.InputField(desc="The abstract of a paper. Your task is to tell for which users this paper might be interesting.")
    user_context: str = dspy.InputField(desc="Descriptions of the users. Use this information to know for which users the paper might be interesting.")

    users: Response = dspy.OutputField(desc="The users for which this paper might be interesting.")

class Recommender(dspy.Module):

    def __init__(self):
        super().__init__(self)
        self.recommender = dspy.TypedChainOfThought(Sig)

    def forward(self, paper_abstract: str):
        return self.recommender(paper_abstract=paper_abstract, user_context="Bojana is a researcher in AI. Victor is a researcher in NLP. Andres is a researcher in CV.")

if __name__ == "__main__":
    set_dspy()
    recommender = Recommender()
    print(recommender("This paper is about transformers."))
