## Generative AI

## What is LLM?
   LLM stands for Large Language Model. These models are designed to understand and generate human-like text based on the input they receive. They are trained on vast amounts of text data and can perform a variety of language-related tasks, such as translation, summarization, and question-answering.

Types Of LLMs:
1. Generates text
   - GPT-3
   - BERT
2. Generated Images and Videos
   - DALL-E
   - Midjourney
3. Generates Music
   - Jukedeck
   - Amper Music
   - TTS 

# Text Generations Before LLMs:
1. Statistical models 
 -- Definition: Statistical models rely on predefined rules and patterns in the data to generate text. They often use techniques like n-grams and Markov chains to predict the next word in a sequence based on the previous words.
 -- Limitations: These models can struggle with understanding context and may produce incoherent or repetitive text, as they do not have a deep understanding of language semantics.
2. Recurring Neural Networks (RNNs)
 -- Definition: RNNs are a type of neural network designed to handle sequential data. They maintain a hidden state that captures information from previous time steps, allowing them to generate text based on the context of the entire sequence.
 -- Limitations: RNNs can suffer from issues like vanishing gradients, making it difficult to learn long-term dependencies in text. They may also produce less coherent text compared to more advanced models.
3. Transformers
 -- Definition: Transformers are a type of neural network architecture that uses self-attention mechanisms to process input data in parallel, rather than sequentially. This allows them to capture long-range dependencies and relationships in text more effectively.
 -- Limitations: While transformers have significantly improved text generation quality, they can be computationally expensive and require large amounts of data for training.
4. Large Language Models (LLMs)
 -- Definition: LLMs are a type of neural network architecture that uses transformers and is trained on massive amounts of text data to generate human-like text.
 -- Limitations: LLMs can be prone to generating biased or inappropriate content, as they learn from the data they are trained on, which may contain biases.

## State of the Art LLMs:
1. GPT-4
 - Description: The latest iteration of OpenAI's Generative Pre-trained Transformer, GPT-4, boasts improved contextual understanding and generation capabilities over its predecessor, GPT-3.
 - Applications: Used in chatbots, content creation, and more.
2. PaLM 2
 - Description: Google's Pathways Language Model (PaLM) 2 is designed to be more efficient and effective in understanding and generating text across various languages and contexts.
 - Applications: Multilingual applications, translation, and content generation.
3. Claude
 - Description: Anthropic's Claude is an AI assistant designed with a focus on safety and user alignment, making it suitable for sensitive applications.
 - Applications: Customer support, content moderation, and more.
4. LLaMA
 - Description: Meta's LLaMA (Large Language Model Meta AI) is designed to be more accessible for researchers and developers, with a focus on ethical AI use.
 - Applications: Research, experimentation, and development of AI applications.

# How LLM Works
 - User Input --> LLM --> Generated Output
 - who is the president of the united states? -->LLM --> The current president of the United States is Joe Biden.

Model and their capabilities:
1. GPT Models(They can only Generate Text or output, They Don't have reasoning capabilities)(thinking capabilities)
 -- Capabilities: Text generation, translation, summarization, question-answering.
 -- Examples: GPT-3, GPT-4
 ## Pros:
 -- High-quality text generation
 -- Versatile applications
 -- Strong contextual understanding
 ## Cons:
    -- Can generate biased or inappropriate content

2. Reasoning Models
 -- Capabilities: Logical reasoning, problem-solving, and decision-making.
 -- Examples: AlphaFold, DeepMind's Gato
 ## Pros:
 -- Strong performance on complex reasoning tasks
 -- Ability to understand and manipulate abstract concepts
 ## Cons:
 -- Limited generalization to new tasks
 -- May require extensive fine-tuning for specific applications


# Important concepts:
# tokens:( )
    - Definition: Tokens are the basic units of text that models process. They can represent words, subwords, or characters, depending on the tokenization strategy used.
    - Importance: Understanding tokens is crucial for grasping how language models interpret and generate text.
    - there's a component named tokenizer which breaks down the text into smaller units called tokens.
# Context:
    - Definition: Context refers to the surrounding information that helps the model understand the meaning of a given input.
    - Importance: Providing adequate context is essential for generating relevant and accurate responses.
    what we send
    1. user Input
    2. instruction
    3. additional information
    4. message history
   - These all are known as context.
# Context Window:
    - Definition: The context window is the maximum amount of text (in tokens) that a model can process at once.
    - Importance: The size of the context window affects the model's ability to understand and generate coherent responses, especially for longer inputs.
    - Example: GPT-3 has a context window of 2048 tokens, while GPT-4 can handle up to 8192 tokens.
    - At max context window size, the model may truncate or omit parts of the input, potentially leading to incomplete or less relevant responses.
What is Knowledge Cutoff?
    - Definition: Knowledge cutoff refers to the point in time when a language model's training data ends, and it no longer has access to information or events occurring after that date.
    - Importance: Understanding knowledge cutoff is crucial for users to gauge the relevance and accuracy of a model's responses, especially for current events or rapidly changing fields.