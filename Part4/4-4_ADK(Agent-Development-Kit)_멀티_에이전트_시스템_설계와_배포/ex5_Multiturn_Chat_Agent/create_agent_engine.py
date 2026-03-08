import vertexai

client = vertexai.Client(project="vertexai-books",location="us-central1",)
memory_bank = client.agent_engines.create()
print(memory_bank)