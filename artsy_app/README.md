Absolutely, here's the content in markdown format:

---

### To run the program:

#### Steps:

1. **Create a Django project:**
   ```bash
   django-admin startproject artsy_app
   cd artsy_app
   ```

2. **Create a Django app within the project:**
   ```bash
   python manage.py startapp artworks
   ```

3. **Install the `requests` package for making HTTP requests:**
   ```bash
   pip install requests
   ```

4. **Run the Django development server on port 5000:**
   ```bash
   python manage.py runserver 0.0.0.0:5000
   ```

#### Exposed endpoints:

- [http://localhost:5000/artworks/get-token/](http://localhost:5000/artworks/get-token/)
- [http://localhost:5000/artworks/get-artworks/](http://localhost:5000/artworks/get-artworks/)

---