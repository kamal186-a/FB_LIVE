name: Live Stream to Facebook & YouTube

on:
  workflow_dispatch:      # مینول بٹن دبا کر چلانے کے لیے (Actions ٹیب سے "Run workflow")
  # schedule:
  #   - cron: "0 18 * * *"   # چاہیں تو خودکار وقت پر چلانے کے لیے یہ لائنز uncomment کریں (UTC ٹائم)

jobs:
  go-live:
    runs-on: ubuntu-latest
    timeout-minutes: 350     # GitHub Actions کی مفت لمٹ کے قریب؛ ضرورت کے مطابق بڑھائیں/گھٹائیں

    steps:
      - name: Repo کو checkout کریں
        uses: actions/checkout@v4

      - name: Python سیٹ اپ کریں
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: ffmpeg انسٹال کریں
        run: sudo apt-get update && sudo apt-get install -y ffmpeg

      - name: Python پیکجز انسٹال کریں
        run: pip install gdown

      - name: لائیو اسٹریم شروع کریں
        run: python live_stream.py
