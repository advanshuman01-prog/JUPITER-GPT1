# JUPITER GPT — शुरुआती बिल्ड

## इसमें अभी क्या काम करता है
- वीडियो फाइल अपलोड (MP4/MOV/MKV/WEBM)
- 3 से 10 क्लिप बनाना
- 9:16 vertical crop और MP4 export
- सभी क्लिप का ZIP डाउनलोड
- बेसिक suggested title/description/hashtags

## जरूरी सीमा
यह पहला working starter है, पूर्ण AI viral-moment detector नहीं। अभी क्लिप्स वीडियो की लंबाई में फैले हुए हिस्सों से बनते हैं; यह बातचीत/भाव/हुक को समझकर सर्वश्रेष्ठ क्षण नहीं चुनता। YouTube URL downloader भी अभी शामिल नहीं है। पहले user-owned/authorized वीडियो अपलोड करके pipeline जाँचें।

## Local run
1. Python 3.11 और FFmpeg इंस्टॉल करें।
2. `pip install -r requirements.txt`
3. `python app.py`
4. Browser में `http://localhost:10000` खोलें।

## Render deploy
1. इस प्रोजेक्ट की सभी फाइलें GitHub repository के root में रखें।
2. Render Dashboard → New + → Blueprint.
3. Repository चुनें और `render.yaml` deploy करें.
4. Render free instances पर बड़े वीडियो, लंबे processing jobs और persistent file storage की सीमाएँ हो सकती हैं। Production के लिए persistent disk/background worker की जरूरत होगी।

## अगला विकास चरण
- YouTube URL ingest (केवल वैध रूप से उपलब्ध/अधिकृत स्रोत)
- Speech-to-text और transcript-based highlight scoring
- Hook / silence / scene-change scoring
- Burned-in Hindi/English subtitles
- Per-clip editable captions और SEO metadata
- Background jobs, progress indicator, persistent storage
- Authentication, rate limits, upload cleanup
