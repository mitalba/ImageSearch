## ⚙️ Setup

1. Clone the project  
```bash
git clone https://github.com/your-username/clothing-clip-fastapi.git
cd clothing-clip-fastapi

2. Install requirements
pip install -r requirements.txt

3. Run the server

uvicorn main:app --reload

4. About Scores

  1.0 → best (almost identical)

  0.8+ → very similar

  0.5 – 0.8 → somewhat similar

  <0.5 → not a good match
