from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import requests
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Tarayıcı ayarlarını yap
chrome_options = Options()
chrome_options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırmak için (isteğe bağlı)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# WebDriver'ı başlat
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# İlgili URL'ye git
url = 'https://www.sahibinden.com/yiyecek-icecek?pagingOffset=20'
driver.get(url)

# Sayfanın tamamen yüklenmesi için bekle
time.sleep(5)

# Dinamik olarak ilanların yüklenmesini beklemek için WebDriverWait kullan
wait = WebDriverWait(driver, 20)  # Bekleme süresini artır
try:
    ilanlar = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.searchResultsItem,.searchResultsLargeThumbnail')))  # Farklı CSS Selector
except Exception as e:
    print(f"Elementler bulunamadı: {e}")
    driver.quit()

# Resim ve açıklamaları saklamak için listeler oluştur
ilan_aciklamalari = []
indirilen_resim_dizinleri = []

# Resimleri indirmek için dizin oluştur
if not os.path.exists('ilan_resimleri'):
    os.makedirs('ilan_resimleri')

# İlanlardan resim ve açıklamaları çek
for index, ilan in enumerate(ilanlar):
    try:
        # Resim URL'sini çek
        resim_eleman = ilan.find_element(By.CSS_SELECTOR, 'img')
        resim_url = resim_eleman.get_attribute('src')
        
        # Resmi indir
        if resim_url:
            response = requests.get(resim_url)
            if response.status_code == 200:
                # Resmi kaydet
                parsed_url = urlparse(resim_url)
                resim_adi = os.path.basename(parsed_url.path)
                resim_yolu = f'ilan_resimleri/ilan_{index}_{resim_adi}'
                with open(resim_yolu, 'wb') as f:
                    f.write(response.content)
                indirilen_resim_dizinleri.append(resim_yolu)
            else:
                indirilen_resim_dizinleri.append(None)
        else:
            indirilen_resim_dizinleri.append(None)
    except Exception as e:
        print(f"Resim indirme hatası: {e}")
        indirilen_resim_dizinleri.append(None)

    try:
        # Açıklamayı çek
        aciklama_eleman = ilan.find_element(By.CSS_SELECTOR, '.searchResultsTitle')
        aciklama = aciklama_eleman.text
        ilan_aciklamalari.append(aciklama)
    except Exception as e:
        print(f"Açıklama çekme hatası: {e}")
        ilan_aciklamalari.append(None)

# Tarayıcıyı kapat
driver.quit()

# Verileri bir DataFrame'e kaydet
df = pd.DataFrame({
    'Resim Dizini': indirilen_resim_dizinleri,
    'Açıklama': ilan_aciklamalari
})

# Veriyi bir CSV dosyasına kaydet
df.to_csv('ilan_resimleri_ve_aciklamalari.csv', index=False)

print("Resimler indirildi ve açıklamalar CSV dosyasına kaydedildi.")
