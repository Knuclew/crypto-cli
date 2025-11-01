import json
import os
import requests
from datetime import datetime

class Renkler:
    YESIL = '\033[92m'
    KIRMIZI = '\033[91m'
    SARI = '\033[93m'
    MAVI = '\033[94m'
    CYAN = '\033[96m'
    BEYAZ = '\033[97m'
    RESET = '\033[0m'
    KALIN = '\033[1m'

class KriptoTakip:
    def __init__(self):
        self.dosya = "takip_listesi.json"
        self.takip_listesi = self.yukle()
        self.coin_listesi = None
    
    def yukle(self):
        """Takip listesini dosyadan yükle"""
        if os.path.exists(self.dosya):
            with open(self.dosya, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Eski format kontrolü (liste ise)
                if isinstance(data, list):
                    print(f"{Renkler.SARI}Eski format tespit edildi, dönüştürülüyor...{Renkler.RESET}")
                    return {}
                return data
        return {}
    
    def kaydet(self):
        """Takip listesini dosyaya kaydet"""
        with open(self.dosya, 'w', encoding='utf-8') as f:
            json.dump(self.takip_listesi, f, ensure_ascii=False, indent=2)
    
    def coin_listesi_yukle(self):
        """CoinGecko'dan tüm coin listesini çek"""
        if self.coin_listesi is not None:
            return
        
        try:
            print(f"{Renkler.CYAN}Coin listesi yükleniyor...{Renkler.RESET}")
            url = "https://api.coingecko.com/api/v3/coins/list"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                self.coin_listesi = response.json()
                print(f"{Renkler.YESIL}Coin listesi yüklendi{Renkler.RESET}")
            else:
                print(f"{Renkler.KIRMIZI}Coin listesi yüklenemedi{Renkler.RESET}")
                self.coin_listesi = []
        except Exception as e:
            print(f"{Renkler.KIRMIZI}Hata: {str(e)}{Renkler.RESET}")
            self.coin_listesi = []
    
    def sembol_ara(self, sembol):
        """Sembole göre coin ID'sini bul"""
        self.coin_listesi_yukle()
        
        sembol = sembol.upper()
        eslesme = None
        
        for coin in self.coin_listesi:
            if coin['symbol'].upper() == sembol:
                if eslesme is None:
                    eslesme = coin
                else:
                    # Birden fazla eşleşme varsa kullanıcıya sor
                    return None
        
        return eslesme
    
    def coin_ekle(self, sembol):
        """Takip listesine coin ekle"""
        coin = self.sembol_ara(sembol)
        
        if coin is None:
            print(f"{Renkler.KIRMIZI}{sembol} bulunamadı veya birden fazla sonuç var{Renkler.RESET}")
            
            # Birden fazla eşleşme varsa göster
            sembol_upper = sembol.upper()
            eslesme_listesi = [c for c in self.coin_listesi if c['symbol'].upper() == sembol_upper]
            
            if len(eslesme_listesi) > 1:
                print(f"\n{len(eslesme_listesi)} sonuç bulundu:")
                for i, c in enumerate(eslesme_listesi[:10], 1):
                    print(f"{i}. {c['name']} ({c['symbol'].upper()}) - ID: {c['id']}")
                
                try:
                    secim = int(input("\nHangisini eklemek istiyorsunuz? (0 = iptal): ").strip())
                    if 1 <= secim <= len(eslesme_listesi):
                        coin = eslesme_listesi[secim - 1]
                    else:
                        print(f"{Renkler.SARI}İptal edildi{Renkler.RESET}")
                        return
                except:
                    print(f"{Renkler.KIRMIZI}Geçersiz seçim{Renkler.RESET}")
                    return
            else:
                return
        
        coin_id = coin['id']
        if coin_id not in self.takip_listesi:
            self.takip_listesi[coin_id] = {
                'name': coin['name'],
                'symbol': coin['symbol'].upper()
            }
            self.kaydet()
            print(f"{Renkler.YESIL}{coin['name']} ({coin['symbol'].upper()}) takip listesine eklendi{Renkler.RESET}")
        else:
            print(f"{Renkler.SARI}{coin['name']} zaten takip listesinde{Renkler.RESET}")
    
    def coin_cikar(self, girdi):
        """Takip listesinden coin çıkar"""
        # Önce ID olarak ara
        if girdi in self.takip_listesi:
            coin_info = self.takip_listesi[girdi]
            del self.takip_listesi[girdi]
            self.kaydet()
            print(f"{Renkler.YESIL}{coin_info['name']} takip listesinden çıkarıldı{Renkler.RESET}")
            return
        
        # Sembol olarak ara
        girdi_upper = girdi.upper()
        for coin_id, info in self.takip_listesi.items():
            if info['symbol'] == girdi_upper:
                del self.takip_listesi[coin_id]
                self.kaydet()
                print(f"{Renkler.YESIL}{info['name']} takip listesinden çıkarıldı{Renkler.RESET}")
                return
        
        print(f"{Renkler.SARI}{girdi} takip listesinde bulunamadı{Renkler.RESET}")
    
    def liste_goster(self):
        """Basit liste göster"""
        if not self.takip_listesi:
            print(f"\n{Renkler.SARI}Takip listeniz boş{Renkler.RESET}\n")
            return
        
        print(f"\n{Renkler.KALIN}TAKİP LİSTESİ{Renkler.RESET}")
        for i, (coin_id, info) in enumerate(self.takip_listesi.items(), 1):
            print(f"{i}. {info['name']} ({info['symbol']})")
        print()
    
    def detayli_goster(self):
        """Detaylı bilgilerle göster"""
        if not self.takip_listesi:
            print(f"\n{Renkler.SARI}Takip listeniz boş{Renkler.RESET}\n")
            return
        
        print(f"\n{Renkler.CYAN}Veriler yükleniyor...{Renkler.RESET}\n")
        
        for coin_id, info in self.takip_listesi.items():
            try:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.coin_detay_yazdir(data)
                else:
                    print(f"{Renkler.KIRMIZI}{info['name']} bilgisi alınamadı{Renkler.RESET}\n")
            except Exception as e:
                print(f"{Renkler.KIRMIZI}{info['name']} için hata: {str(e)}{Renkler.RESET}\n")
    
    def coin_detay_yazdir(self, data):
        """Coin detaylarını formatla ve yazdır"""
        print(f"{Renkler.KALIN}{Renkler.MAVI}{data['name']} ({data['symbol'].upper()}){Renkler.RESET}")
        
        market = data.get('market_data', {})
        
        # Fiyat Bilgileri
        fiyat_usd = market.get('current_price', {}).get('usd', 0)
        fiyat_try = market.get('current_price', {}).get('try', 0)
        print(f"Fiyat (USD): ${fiyat_usd:,.4f}")
        print(f"Fiyat (TRY): ₺{fiyat_try:,.2f}")
        
        # Değişim Yüzdeleri
        degisim_24s = market.get('price_change_percentage_24h', 0)
        degisim_7g = market.get('price_change_percentage_7d', 0)
        degisim_30g = market.get('price_change_percentage_30d', 0)
        
        print(f"\nDeğişimler:")
        print(f"  24 Saat: {self.renk_ver(degisim_24s)}%")
        print(f"  7 Gün:   {self.renk_ver(degisim_7g)}%")
        print(f"  30 Gün:  {self.renk_ver(degisim_30g)}%")
        
        # Piyasa Verileri
        mcap = market.get('market_cap', {}).get('usd', 0)
        volume = market.get('total_volume', {}).get('usd', 0)
        rank = data.get('market_cap_rank', 'N/A')
        
        print(f"\nPiyasa Verileri:")
        print(f"  Piyasa Değeri: ${mcap:,.0f}")
        print(f"  24s Hacim: ${volume:,.0f}")
        print(f"  Sıralama: #{rank}")
        
        # ATH/ATL
        ath = market.get('ath', {}).get('usd', 0)
        atl = market.get('atl', {}).get('usd', 0)
        print(f"\nEn Yüksek/Düşük:")
        print(f"  ATH: ${ath:,.4f}")
        print(f"  ATL: ${atl:,.4f}")
        
        # Arz Bilgileri
        circulating = market.get('circulating_supply', 0)
        total = market.get('total_supply', 0)
        max_supply = market.get('max_supply', 0)
        
        print(f"\nArz Bilgileri:")
        print(f"  Dolaşımdaki: {circulating:,.0f}")
        if total:
            print(f"  Toplam: {total:,.0f}")
        if max_supply:
            print(f"  Maksimum: {max_supply:,.0f}")
        
        print()
    
    def renk_ver(self, deger):
        """Pozitif/negatif değerlere göre renklendirme"""
        if deger > 0:
            return f"{Renkler.YESIL}+{deger:.2f}{Renkler.RESET}"
        elif deger < 0:
            return f"{Renkler.KIRMIZI}{deger:.2f}{Renkler.RESET}"
        else:
            return f"{deger:.2f}"

def menu():
    """Ana menüyü göster"""
    print(f"\n{Renkler.KALIN}KRİPTO TAKİP UYGULAMASI{Renkler.RESET}")
    print("1. Takip listesine ekleme/çıkarma")
    print("2. Takip listesini görüntüle")
    print("3. Detaylı bilgilerle görüntüle")
    print("0. Çıkış")

def main():
    tracker = KriptoTakip()
    
    while True:
        menu()
        secim = input("\nSeçiminiz: ").strip()
        
        if secim == "1":
            print("\n[1] Ekle  [2] Çıkar")
            alt_secim = input("Seçiminiz: ").strip()
            
            if alt_secim == "1":
                sembol = input("Eklenecek coin sembolü (örn: BTC, ETH): ").strip()
                tracker.coin_ekle(sembol)
            elif alt_secim == "2":
                sembol = input("Çıkarılacak coin sembolü veya ID: ").strip()
                tracker.coin_cikar(sembol)
            else:
                print(f"{Renkler.KIRMIZI}Geçersiz seçim{Renkler.RESET}")
        
        elif secim == "2":
            tracker.liste_goster()
        
        elif secim == "3":
            tracker.detayli_goster()
        
        elif secim == "0":
            print(f"\n{Renkler.CYAN}Görüşmek üzere{Renkler.RESET}")
            break
        
        else:
            print(f"{Renkler.KIRMIZI}Geçersiz seçim{Renkler.RESET}")

if __name__ == "__main__":
    main()