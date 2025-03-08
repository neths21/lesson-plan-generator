import google.generativeai as genai

genai.configure(api_key="AIzaSyCMRmlBhSry38aigqjS3H1fzxj4KjHLfaQ")  # Replace with your actual API key

models = genai.list_models()
for model in models:
    print(model.name)
