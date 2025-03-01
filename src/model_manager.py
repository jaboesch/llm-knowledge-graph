from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings


class ModelManager:
    def __init__(
        self, hf_token, chat_model="meta-llama/Llama-3.3-70B-Instruct", max_new_tokens=4096, embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    ):
        if chat_model == "gpt-4o":
            self.chat = ChatOpenAI(model="gpt-4o", temperature=0.1)
        else:
            # HuggingFace tool calling is currently not working for GraphReader, but it works well for graph building.
            llm = HuggingFaceEndpoint(
                repo_id=chat_model,
                task="text-generation",
                max_new_tokens=max_new_tokens,
                timeout=420,
                do_sample=False,
                repetition_penalty=1.03,
                temperature=0.1,
                huggingfacehub_api_token=hf_token,
            )
            self.chat = ChatHuggingFace(llm=llm)
        
        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=hf_token, model_name=embedding_model
        )
        