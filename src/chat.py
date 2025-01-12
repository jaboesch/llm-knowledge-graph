from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


class Chat:
    def __init__(
        self, hf_token, model="meta-llama/Llama-3.3-70B-Instruct", max_new_tokens=2500
    ):
        llm = HuggingFaceEndpoint(
            repo_id=model,
            task="text-generation",
            max_new_tokens=max_new_tokens,
            timeout=300,
            do_sample=False,
            repetition_penalty=1.03,
            temperature=0.1,
            huggingfacehub_api_token=hf_token,
        )
        self.chat = ChatHuggingFace(llm=llm)
