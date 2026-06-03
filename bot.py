import os

print("BOT BAŞLADI")

token = os.getenv("BOT_TOKEN")

print("TOKEN VAR:", bool(token))
print("TOKEN UZUNLUK:", len(token) if token else 0)

raise Exception("TEST DURDURMA")
