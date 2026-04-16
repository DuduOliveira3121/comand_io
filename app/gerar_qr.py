import qrcode
import os

# URL completa para funcionar no celular
base_url = "http://192.168.15.73:5000"

# Garantir que a pasta qrcodes existe na raiz do projeto
os.makedirs("qrcodes", exist_ok=True)

for mesa in range(1, 11):
    url = f"{base_url}/mesa/{mesa}"
    img = qrcode.make(url)
    img.save(f"qrcodes/mesa_{mesa}.png")
    print(f"✅ QR da mesa {mesa} criado: {url}")

print(f"\n✅ Todos os {10} QR-Codes foram gerados em qrcodes/")
    
print(f"\n💡 Se os QR-Codes não funcionarem, mude a URL base no .env")
print(f"   Exemplo: QR_BASE_URL=http://192.168.1.100:5000")