# vertex-langchain-callback

This is an example of how to use the langchain library to answer questions about a paragraph of text. 

## Sample Output

The output of this example will be a JSON object with the following fields:

* `answer`: The answer to the question, either `true` or `false`.
* `reasoning`: The reasoning behind the answer.

Once the chain is completed, the callbackhandler will run ensure that it sees true/false in the response from the llm. If it doesn't it will try to run the chain again. 

Depending on the response from llm it will ensure it generates a properly generates JSON.

It also has the ability to change the prompt for the retries.

