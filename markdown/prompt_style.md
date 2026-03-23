# Prompt Style

## Alpaca Prompt Style
Alpaca is a fine-tuned version of Meta's LLaMA 7B model, trained on 52K instruction-following demonstrations. The Alpaca prompt style typically includes a clear instruction followed by an input and an expected output. Here's an example of the Alpaca prompt style:

### instructions:<System Prompt>\n
### input:<User Prompt>\n
### Response:<Expected Output>\n


# ChatML Prompt Style
ChatML is a markup language designed for structuring chat-based interactions with language models. It allows
for clear delineation of roles (system, user, assistant) and message types. Here's an example of the ChatML prompt style:
{
    "messages": [
        {"role": "system", "content": "<System Prompt>"},
        {"role": "user", "content": "<User Prompt>"},
        {"role": "assistant", "content": "<Expected Output>"}
    ]
}

Open AI, GEmini uses ChatML prompt style.

# instruction Prompting (LLaMA 2 uses this style)
Instruction prompting involves providing the model with a specific instruction or task to perform. This style is often used in models like LLaMA 2. Here's an example of instruction prompting:
### Instruction: <System Prompt>\n
### Input: <User Prompt>\n
### Response: <Expected Output>\n




