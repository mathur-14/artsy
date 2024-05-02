
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

3. **Install the packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **To set up cron job:**
   ```bash
   python manage.py crontab add
   ```

5. **Run the Django development server on port 5000:**
   ```bash
   python manage.py runserver 0.0.0.0:5000
   ```

#### Exposed endpoints:

- [http://localhost:5000/artworks/get-token/](http://localhost:5000/artworks/get-token/)
- [http://localhost:5000/artworks/put-artworks/](http://localhost:5000/artworks/put-artworks/)
- [http://localhost:5000/artworks/get-paginated-artworks/](http://localhost:5000/artworks/get-paginated-artworks/)
- [http://localhost:5000/artworks/get-artists/](http://localhost:5000/artworks/get-artists/)
- [http://localhost:5000/artworks/get-artwork-id/<str:id>/](http://localhost:5000/artworks/get-artwork-id/<str:id>/)
- [http://localhost:5000/artworks/get-artworks-category/<str:category>/](http://localhost:5000/artworks/get-artworks-category/<str:category>/)
- [http://localhost:5000/artworks/get-artworks-by-artist/<str:artist_id>/](http://localhost:5000/artworks/get-artworks-by-artist/<str:artist_id>/)
- [http://localhost:5000/artworks/get-categories/](http://localhost:5000/artworks/get-categories/)

---