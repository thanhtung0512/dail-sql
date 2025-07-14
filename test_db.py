import json
import openai
import time
from utils.enums import LLM

# 👉 Copy nguyên code hàm init_chatgpt, ask_completion, ask_chat, ask_llm vào đây

def init_chatgpt(OPENAI_API_KEY, OPENAI_GROUP_ID, model=None):
    openai.api_key = OPENAI_API_KEY
    openai.organization = OPENAI_GROUP_ID  # Nếu không có cũng được
    openai.api_base = "https://api.yescale.io/v1"


def ask_completion(model, batch, temperature):
    response = openai.Completion.create(
        model=model,
        prompt=batch[0],
        temperature=temperature,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=[";"]
    )
    response_clean = [_["text"] for _ in response["choices"]]
    return dict(
        response=response_clean,
        **response["usage"]
    )


def ask_chat(model, messages: list, temperature, n):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=200,
        n=n
    )
    response_clean = [choice["message"]["content"] for choice in response["choices"]]
    if n == 1:
        response_clean = response_clean[0]
    return dict(
        response=response_clean,
        **response["usage"]
    )


def ask_llm(model: str, batch: list, temperature: float, n: int):
    n_repeat = 0
    while True:
        try:
            if model in LLM.TASK_COMPLETIONS:
                assert n == 1
                response = ask_completion(model, batch, temperature)
            elif model in LLM.TASK_CHAT:
                assert len(batch) == 1, "batch must be 1 in this mode"
                messages = [{"role": "user", "content": batch[0]}]
                response = ask_chat(model, messages, temperature, n)
                response['response'] = [response['response']]
            break
        except openai.error.RateLimitError:
            n_repeat += 1
            print(f"Repeat for the {n_repeat} times for RateLimitError")
            time.sleep(1)
            continue
        except json.decoder.JSONDecodeError:
            n_repeat += 1
            print(f"Repeat for the {n_repeat} times for JSONDecodeError")
            time.sleep(1)
            continue
        except Exception as e:
            n_repeat += 1
            print(f"Repeat for the {n_repeat} times for exception: {e}")
            time.sleep(1)
            continue

    return response


if __name__ == "__main__":
    # ✅ Init API
    init_chatgpt(
        OPENAI_API_KEY="sk-jpWR1cYJW7gqbxzuGtcPHv5CVA4xXm5oa3DikbAKxZrTkVxL",
        OPENAI_GROUP_ID=""  # Hoặc ""
    )



    # ✅ Chạy test Chat API
    print("\n🎯 TEST Chat API")
    result = ask_llm(
        model="gpt-4",
        batch=["Explain how photosynthesis works."],
        temperature=0.0,
        n=1
    )["response"][0].strip()
    
    print(result)
