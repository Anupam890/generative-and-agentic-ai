from google import genai

client = genai.Client(
    api_key="AIzaSyAwTbeOvZPE0vpgpDIvEgZBlc_KvMmCzok"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",    contents="Write a poem about the sea in the style of Shakespeare.",
)
print(response.text)