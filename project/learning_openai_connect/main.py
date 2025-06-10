import os 
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    print("Hello from learning-openai-connect!")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "ユニコーンについて、1文だけのおやすみ前の物語を書いてください。"}
        ]
    )

    print(response["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
