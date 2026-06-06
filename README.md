# CV RAG Assistant

Basit bir CV bazlı Retrieval-Augmented-Generation (RAG) örneği.

**Dosyalar**

- `index.py` — `cv.txt` içeriğini parçalayıp OpenAI ile embedding oluşturur ve Chroma DB'ye yazar.
- `app.py` — Chroma DB'den ilgili dokümanları çekip LLM ile soruları cevaplar.
- `cv.txt` — İndexlenecek CV metni (kendi dosyanı ekle).
- `requirements.txt` — Gerekli paketler.
- `.env.example` — Ortam değişkeni format örneği.

**Önkoşullar**

- Python 3.10+ (veya proje ortamındaki sürüm)
- Sanal ortam (tercihen `venv`)
- OpenAI API anahtarı

Kurulum ve Çalıştırma

1. Proje dizinine gir ve sanal ortamı aktif et:

```bash
cd /Users/user/cv-rag-assistant
source venv/bin/activate
```

2. Bağımlılıkları kur (gerekiyorsa):

```bash
pip install -r requirements.txt
```

3. OpenAI API anahtarını ayarla (terminal oturumuna geçici olarak):

```bash
export OPENAI_API_KEY="sk-YENI_API_ANAHTARINIZ"
```

Alternatif olarak, `.env` dosyası oluşturup içine ekleyebilirsin (`.gitignore` zaten `.env`'i yoksayar). Örnek dosya için `.env.example` dosyasını kullanabilirsin.

4. `cv.txt` dosyasına CV metnini koy.

5. İndex oluştur (sadece bir kez):

```bash
python index.py
```

6. Sohbet uygulamasını çalıştır:

```bash
python app.py
```

Kullanım

- `index.py` çalıştıktan sonra `./db` içinde `cv` koleksiyonu oluşturulur.
- `app.py` çalıştığında `Ask:` istemi gelir; soru yaz ve Enter'a bas.

Güvenlik Notları

- OpenAI anahtarını git deposuna veya herkese açık yerlere koyma.
- Eğer anahtar kazara paylaşıldıysa OpenAI hesabından derhal iptal (revoke) et ve yenisini oluştur.

Sorun olursa bana söyle, test etmek veya hata ayıklamak için yardımcı olurum.
