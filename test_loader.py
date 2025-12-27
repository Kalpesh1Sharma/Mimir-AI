from backend.assistant import MimirAssistant

mimir = MimirAssistant()

# Upload files
mimir.ingest_files(["test.txt"])

# Ask about file
print(mimir.query("What was the college fest about?"))

# Clear session
mimir.clear_files()

# Ask normal RAG
print(mimir.query("What is FAISS?"))

# Ask live IPL (should refuse)
print(mimir.query("What happened yesterday in IPL?"))
