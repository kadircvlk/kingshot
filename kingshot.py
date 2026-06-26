import threading
import requests
import json

# 1. AYARLAR VE CURL VERİLERİ
LOOKUP_API_TEMPLATE = "https://kingshot.net/api/player-info?playerId={}" 
REDEEM_API = "https://kingshot.net/api/gift-codes/redeem"  

# Aynı anda çalışacak eş zamanlı istek sayısı
THREAD_SAYISI = 10  

# Tarayıcından kopyaladığın birebir çalışan gizli çerezler (Cloudflare bypass için)
COOKIE_STRING = (
    "_ga=GA1.1.1681672499.1782403395; "
    "cf_clearance=VBGOQYAQBEParZduNmaTFCmO8jH71pj3h6QYE.gXCsE-1782413784-1.2.1.1-FL1lhhcWlMkMWPpTzsR_1JinnOjrhcBfGwWSiX6.0N75.8nObfrtB13odiVvci2JUesZ2fbtGh_8EYmkiX1MgqVGQE9eWuInWcZmKAEGFtfAMN7vKkXQpQPsoxtZ2AC8vcxq1Pn_dkSyCNvn5OdPXfw3mOId1VWTNK5wXNr7ASgPkFtMRUyrZEci2pEGyhWcckAJU78vJfevD8pKWY2OEDQpzw9rdzwaEA2XCzUL4Rv1Mk1ntgrw9Fl_HjCtbjz4j7J5YxwzcZyZOtwmQhPXyftNoNkwls7QHBWCEYJrVAoENYkLrucQ75sz3DSWeMsPEeU13Z4v5t8DGArYBC7Rww; "
    "__Host-next-auth.csrf-token=818a3f4ee33ca49b831d92947266daef089c4e40534f43455d05571fd79c1f96%7C9b58e3023d62dbf71a9df0cb87dd9804493984e3225dfb2f82919ff31aae91ae; "
    "__Secure-next-auth.callback-url=https%3A%2F%2Fkingshot.net; "
    "_ga_XJTK288X1N=GS2.1.s1782413784$o2$g1$t1782413894$j42$l0$h0"
)

def gift_code_redeem_task(thread_id, player_id, gift_code):
    session = requests.Session()
    
    # cURL isteğindeki tüm başlıkları (Headers) eksiksiz taklit ediyoruz
    headers = {
        "authority": "kingshot.net",
        "accept": "*/*",
        "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "cookie": COOKIE_STRING,
        "origin": "https://kingshot.net",
        "referer": "https://kingshot.net/tr/gift-codes/redeem",
        "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
    }
    session.headers.update(headers)

    try:
        # ADIM 1: Oyuncu Doğrulama (Zaten çalışıyordu)
        lookup_url = LOOKUP_API_TEMPLATE.format(player_id)
        lookup_response = session.get(lookup_url, timeout=5)
        
        if lookup_response.status_code == 200:
            print(f"[Thread-{thread_id}] Oyuncu doğrulandı. Eş zamanlı kod basılıyor...")
            
            # ADIM 2: cURL Yapısıyla Birebir Eşleşen Veri Paketi
            # cURL çıktında playerId string ("3351...") olarak gönderilmiş, aynısını yapıyoruz.
            redeem_payload = {
                "playerId": str(player_id),
                "giftCode": str(gift_code).strip()
            }
            
            # Boşluksuz saf JSON string haline getiriyoruz (Sunucunun sevdiği format)
            ham_veri = json.dumps(redeem_payload, separators=(',', ':'))
            
            # EŞ ZAMANLI İSTEK ATEŞLEME
            redeem_response = session.post(REDEEM_API, data=ham_veri, timeout=5)
            
            # Sonucu ekrana bas
            print(f"[Thread-{thread_id}] Sunucu Yanıtı ({redeem_response.status_code}): {redeem_response.text}")
        else:
            print(f"[Thread-{thread_id}] Oyuncu doğrulanamadı. Durum: {lookup_response.status_code}")

    except Exception as e:
        print(f"[Thread-{thread_id}] Bağlantı hatası: {e}")

if __name__ == "__main__":
    print("=== KINGSHOT SIFIR HATA MULTITHREAD BOT ===")
    
    girilen_player_id = input("Lütfen Oyuncu ID (Player ID) girin: ").strip()
    girilen_gift_code = input("Lütfen Kullanılacak Hediye Kodunu girin: ").strip()
    
    if not girilen_player_id or not girilen_gift_code:
        print("\nHata: Alanlar boş bırakılamaz!")
        exit()

    print("\n--------------------------------------------------")
    print(f"{THREAD_SAYISI} adet thread cURL taklidiyle beklemesiz başlatılıyor...")
    print("--------------------------------------------------\n")

    threads = []
    for i in range(THREAD_SAYISI):
        t = threading.Thread(
            target=gift_code_redeem_task, 
            args=(i+1, girilen_player_id, girilen_gift_code)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n[✓] Eş zamanlı tüm işlemler başarıyla bitti!")
