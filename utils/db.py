from pymongo import MongoClient

# Substitua pela URL do seu cluster MongoDB (por exemplo, MongoDB Atlas)
MONGO_URI = "mongodb+srv://eduardobrito28:M1ngo1984@cluster0.mxlgh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Ou URI do Atlas

client = MongoClient(MONGO_URI)
db = client["chatbot_db"]  # Nome do banco
documents_collection = db["documents"]
chats_collection = db["chats"]
