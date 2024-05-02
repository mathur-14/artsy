
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
- [http://localhost:5000/artworks/get-artwork-id/:id/](http://localhost:5000/artworks/get-artwork-id/:id/)
- [http://localhost:5000/artworks/get-artworks-category/:category/](http://localhost:5000/artworks/get-artworks-category/:category/)
- [http://localhost:5000/artworks/get-artworks-by-artist/:artist_id>/](http://localhost:5000/artworks/get-artworks-by-artist/:artist_id/)
- [http://localhost:5000/artworks/get-categories/](http://localhost:5000/artworks/get-categories/)

---

---

## API Documentation

### 1. Generate Token
- **Endpoint**: `http://localhost:5000/artworks/get-token/`
- **Usage**: Internal use only; generates a token to access Artsy APIs.
- **Response Body**:
  ```
  {"token": "<generated_token>"}
  ```

### 2. Populate Artworks
- **Endpoint**: `http://localhost:5000/artworks/put-artworks/`
- **Usage**: Populates artworks in MongoDB using resources from the Artsy public API `/artwork`. Artists for each artwork are also populated.
- **Response Body**:
  ```
  {"message": "Artworks populated successfully."}
  ```

### 3. Get Paginated Artworks
- **Endpoint**: `http://localhost:5000/artworks/get-paginated-artworks/`
- **Usage**: Fetches artworks from MongoDB in a paginated manner with a page size of 10.
- **Response Body**:
  ```json
  {
      "count": 26070,
      "next": true,
      "previous": false,
      "results": [
          {
              "id": "4d8b92eb4eb68a1b2c000968",
              "slug": "gustav-klimt-der-kuss-the-kiss",
              "title": "Der Kuss (The Kiss)",
              "category": "Painting",
              "medium": "Oil and gold leaf on canvas",
              "date": "1907-1908",
              "dimensions": {
                  "in": {
                      "text": "70 9/10 × 70 9/10 in",
                      "height": 70.9,
                      "width": 70.9,
                      "depth": null,
                      "diameter": null
                  },
                  "cm": {
                      "text": "180.1 × 180.1 cm",
                      "height": 180.1,
                      "width": 180.1,
                      "depth": null,
                      "diameter": null
                  }
              },
              "additional_information": "[Image source](https://commons.wikimedia.org/wiki/File:Klimt_-_The_Kiss.jpg)",
              "_links": {
                  "thumbnail": {
                      "href": "https://d32dm0rphc51dk.cloudfront.net/NOpIAwQa-3r51Cg9qXKbfA/medium.jpg"
                  },
                  "self": {
                      "href": "https://api.artsy.net/api/artworks/4d8b92eb4eb68a1b2c000968"
                  },
                  "similar_artworks": {
                      "href": "https://api.artsy.net/api/artworks?similar_to_artwork_id=4d8b92eb4eb68a1b2c000968"
                  }
              },
              "artists": [
                  {
                      "id": "4d8b92b64eb68a1b2c000414",
                      "name": "Gustav Klimt",
                      "gender": "male",
                      "birthday": "1862",
                      "deathday": "1918",
                      "nationality": "Austrian",
                      "artworks": "https://api.artsy.net/api/artworks?artist_id=4d8b92b64eb68a1b2c000414",
                      "similar_artists": "https://api.artsy.net/api/artists?similar_to_artist_id=4d8b92b64eb68a1b2c000414"
                  }
              ]
          },
          ...
      ]
  }
  ```

### 4. Get Artists
- **Endpoint**: `http://localhost:5000/artworks/get-artists/`
- **Usage**: Returns a list of artists by ID and name.
- **Response Body**:
  ```json
  [
      {
          "name": "Adam van Breen",
          "id": "515cffa3b5907bf7e8001e09"
      },
      ...
  ]
  ```

### 5. Get Artwork by ID
- **Endpoint**: `http://localhost:5000/artworks/get-artwork-id/:id/`
- **Usage**: Retrieves details of a specific artwork based on its ID.
- **Response Body**:
  ```json
  {
      "id": "515b169638ad2d78ca00093f",
      "slug": "possibly-agnolo-bronzino-the-fall-of-phaethon",
      "title": "The Fall of Phaethon",
      "category": "Drawing, Collage or other Work on Paper",
      "medium": "Black chalk on laid paper",
      "date": "1555/1559",
      "dimensions": {
          "in": {
              "text": "16 × 10 11/16 in",
              "height": 16.0,
              "width": 10.6875,
              "depth": null,
              "diameter": null
          },
          "cm": {
              "text": "40.6 × 27.1 cm",
              "height": 40.6,
              "width": 27.1,
              "depth": null,
              "diameter": null
          }
      },
      "additional_information": "\r\n    overall: 40.7 x 27.2 cm (16 x 10 11/16 in.)\r\n    ",
      "_links": {
          "thumbnail": {
              "href": "https://d32dm0rphc51dk.cloudfront.net/SO-YClCqWhosku5HQ3HFTw/medium.jpg"
          },
          "self": {
              "href": "https://api.artsy.net/api/artworks/515b169638ad2d78ca00093f"
          },
          "similar_artworks": {
              "href": "https://api.artsy.net/api/artworks?similar_to_artwork_id=515b169638ad2d78ca00093f"
          }
      },
      "artists": [
          {
              "id": "515d62d45eeb1c904c0046e9",
              "name": "After Michelangelo",
              "gender": "",
              "birthday": "",
              "deathday": "",
              "nationality": "",
              "artworks": "https://api.artsy.net/api/artworks?artist_id=515d62d45eeb1c904c0046e9",
              "similar_artists": "https://api.artsy.net/api/artists?similar_to_artist_id=515d62d45eeb1c904c0046e9"
          },
          ...
      ]
  }
  ```

### 6. Get Artworks by Category
- **Endpoint**: `http://localhost:5000/artworks/get-artworks-category/:category/`
- **Usage**: Returns paginated results of artworks based on a specified category.
- **Response Body**: Same as `Get Paginated Artworks`.

### 7. Get Artworks by Artist
- **Endpoint**: `http://

localhost:5000/artworks/get-artworks-by-artist/:artist_id>/`
- **Usage**: Searches MongoDB for artworks by a specific artist.
- **Response Body**: Same as `Get Paginated Artworks`.

### 8. Get Categories
- **Endpoint**: `http://localhost:5000/artworks/get-categories/`
- **Usage**: Returns a list of categories used by the artworks.
- **Response Body**:
  ```json
  [
      null,
      "",
      "Architecture",
      "Books and Portfolios",
      "Design/Decorative Art",
      "Drawing, Collage or other Work on Paper",
      "Mixed Media",
      "Other",
      "Painting",
      "Photography",
      "Posters",
      "Print",
      "Sculpture",
      "Textile Arts"
  ]
  ```

#### Note:
- For paginated endpoints, use `?page=n` for page navigation.
- Response bodies are structured according to their respective API functionalities.