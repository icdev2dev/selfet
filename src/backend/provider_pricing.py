import yaml

providers_yaml = """
openai:
    gpt-3.5-turbo-0613:
        1.5,2
    gpt-3.5-turbo-16k-0613:
        3,4
    gpt-4-turbo: 
        10,30
    gpt-4:
        30,60

groq:
    llama3-70b-8192:
        0.59,0.79
    llama3-8b-8192:
        0.05,0.08
    mixtral-8x7b-32768:
        0.24,0.24
    gemma-7b-i:
        0.07, 0.07
"""

PROVIDER_PRICING = yaml.safe_load(providers_yaml)
