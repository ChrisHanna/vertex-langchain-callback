import os
import sys
import re
import io
import json
import langchain
import json
from typing import Dict, Union, Any, List
from langchain.llms import VertexAI
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.base import BaseCallbackHandler

questionAndParagraph = """Question: Is the sky blue?

    The color of the sky is a result of the way sunlight interacts with the atmosphere. Sunlight is made up of all the colors of the rainbow, but when it passes through the atmosphere, some of the colors are scattered more than others. Blue light is scattered more than other colors because it travels as shorter, smaller waves. This is why the sky appears blue during the day.

    At sunrise and sunset, the sun is lower in the sky, so the sunlight has to travel through more of the atmosphere to reach our eyes. This means that more of the blue light is scattered away, and the remaining light appears redder. This is why the sky appears red at sunrise and sunset.

    The color of the sky can also be affected by pollution and other particles in the atmosphere. These particles can scatter sunlight in different ways, which can cause the sky to appear different colors. For example, the sky may appear hazy or smoky if there is a lot of pollution in the air.
    """

prompt_template = """
    Answer the question about the following paragraph: 
    {paragraph}

    Output format must be a json dictionary
    answer: true or false,
    reasoning: why true or false was chosen as an answer
    """   

retry_prompt = """Answer the question about the following paragraph: 
    {paragraph} 
    
    Output format must be a json dictionary
    <string name="answer" description="true or false" />
    <string name="reasoning" description="reasoning behind true or false answer" />
    """

retryCount = 0

def run_true_or_false():

    responseHandler = EnsureTrueOrFalseHandler()

    llm = VertexAI(temperature=0, max_output_tokens=1024)
    
    llm_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template)
    )

    llm_chain(questionAndParagraph, callbacks=[responseHandler])
    
    return responseHandler.returnValues

class EnsureTrueOrFalseHandler(BaseCallbackHandler):
    def __init__(self):
        self.returnValues = None

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        answer = None
        reasoning = None
      
        if 'text' not in outputs:
            answer = "error"
            reasoning = "could not find text in answer"

        try:
            data = json.loads(outputs['text'])
        except json.JSONDecodeError:
            answer = "error"
            reasoning = "could not find text in outputs"
        else:
            if 'answer' in data:
                if 'true' in str(data['answer']).lower():
                    answer = True
                elif 'false' in str(data['answer']).lower():
                    answer = False
                else:
                    answer = "error"
                    reasoning = "could not find true/false in answer"

            if 'reasoning' in data:
                reasoning = data['reasoning']

            if answer is None:
                    answer = "error"
                    reasoning = "answer was not set"
            if reasoning is None:
                    answer = "error"
                    reasoning = "reasoning was not set"

            result = {
                'answer': answer,
                'reasoning': reasoning
            }

            self.returnValues = json.dumps(result)

    def get_return_values(self):
        return self.returnValues
    
if __name__ == '__main__':
    result = run_true_or_false()

    result_dict = json.loads(result)
    answer = result_dict.get('answer')

    if answer == 'error' and retryCount <= 3:
        result = run_true_or_false()
        retryCount += 1
        prompt_template = retry_prompt

    print(result)
