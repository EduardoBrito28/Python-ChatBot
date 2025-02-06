from pymongo import MongoClient
import gridfs

# Substitua pela URL do seu cluster MongoDB (por exemplo, MongoDB Atlas)
MONGO_URI = "mongodb+srv://eduardobrito28:M1ngo1984@cluster0.mxlgh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["chatbot_db"]  # Nome do banco

# Inicializando o GridFS
fs = gridfs.GridFS(db)

# Coleções existentes
documents_collection = db["documents"]
chats_collection = db["chats"]
users_collection = db["users"]

def create_user(nome, email, departamento, empresa, senha, nivel_acesso):
    if users_collection.find_one({"email": email}):
        return False
    user_data = {
        "nome": nome,
        "email": email,
        "departamento": departamento,
        "empresa": empresa,
        "senha": senha,
        "nivel_acesso": nivel_acesso
    }
    users_collection.insert_one(user_data)
    return True

def get_user(email):
    return users_collection.find_one({"email": email})