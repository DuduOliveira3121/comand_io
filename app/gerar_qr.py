import qrcode

base_url = "http://192.168.15.2:5500/frontend/mesa.html?mesa="

for mesa in range(1, 11):

    url = base_url + str(mesa)

    img = qrcode.make(url)

    img.save(f"mesa_{mesa}.png")

    print(f"QR da mesa {mesa} criado")