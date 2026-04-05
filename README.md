# ai-fraud-management-system-play

FastAPI tabanlı sahtecilik (fraud) shadow modu API: Random Forest modeli, Stripe webhook, shadow loglama ve isteğe bağlı Supabase entegrasyonu.

## Çalıştırma

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Supabase anahtarlarını doldurun
uvicorn app.main:app --reload
```

## Test

```bash
python test_model.py
```

## GitHub remote (ilk push)

Yerelde commit hazırsa GitHub’da **boş** `ai-fraud-management-system-play` reposu oluşturun, ardından:

```bash
git remote add origin https://github.com/<KULLANICI>/ai-fraud-management-system-play.git
git branch -M main
git push -u origin main
```
