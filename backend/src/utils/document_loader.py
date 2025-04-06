import os

def load_and_chunk_documents(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), encoding="utf-8") as f:
                content = f.read()
                # Simple chunking: split every 1000 characters
                chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                docs.extend(chunks)
    return docs
