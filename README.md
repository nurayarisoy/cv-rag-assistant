# CV RAG Assistant

Bu proje yerel model tabanlı bir CV arama ve cevaplama uygulamasıdır.

## Dosyalar

- `index.py` — `cv.txt` içeriğini parçalayıp yerel embedding modeliyle vektörler oluşturur ve Chroma DB'ye yazar.
- `app.py` — Chroma DB'den ilgili dokümanları çekip yerel LLM ile sorulara cevap verir.
- `web.py` — Flask tabanlı web arayüzü.
- `cv.txt` — İndexlenecek CV metni.
- `requirements.txt` — Gerekli Python paketleri.

## Gereksinimler

- Python 3.10+
- `venv` veya benzeri sanal ortam

## Kurulum

```bash
cd /Users/user/cv-rag-assistant
source venv/bin/activate
pip install -r requirements.txt
```

## Kullanım

1. `cv.txt` dosyasına CV metnini ekleyin.
2. `index.py` ile vektör veritabanını oluşturun:

```bash
python index.py
```

3. CLI uygulamasını çalıştırın:

```bash
python app.py
```

4. Web arayüzünü başlatın:

```bash
python web.py
```

5. Tarayıcıda `http://127.0.0.1:5000` adresine gidin.

## Notlar

- Bu sürüm OpenAI API gerektirmez.
- Model dosyaları internetten indirilecektir.
- Eğer `google/flan-t5-small` çok ağır gelirse, daha küçük bir `text2text-generation` modeline geçebilirsiniz.
