import tiktoken

enc = tiktoken.encoding_for_model("gpt-4")

text = "Hey There, I am Anupam Mandal, a software developer!"
tokens = enc.encode(text)
print(tokens)

# Decoding the tokens back to text
decoded_text = enc.decode(tokens)
print(decoded_text)