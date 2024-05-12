from django.http import JsonResponse
from django.core.paginator import Paginator
from .helper import setup_session
import subprocess
from artsy_app.settings import db
import json
import time
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pymongo import MongoClient
import json
import time
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import explode, lower, regexp_replace, split, col, rand, avg
import nltk
from nltk.corpus import stopwords
from pyspark.sql import functions as F

artwork_projection = {
    '_id': 0,
    'id': 1,
    'slug': 1,
    'title': 1,
    'category': 1,
    'additional_information': 1,
    'medium': 1,
    'date': 1,
    'dimensions': 1,
    'artists': 1,
    '_links.thumbnail.href': 1,
    '_links.self.href': 1,
    '_links.similar_artworks.href': 1,
}

def get_token(request):
    # Parameters for obtaining user token
    cid = '6bb5b39fa796dfeccfdb'
    cs = '7a1bf2224a3b2aafb0cfcb0c141888fb'
    token_url = f'https://api.artsy.net/api/tokens/xapp_token?client_id={cid}&client_secret={cs}'

    curl_command = ["curl", "-v", "-X", "POST", token_url]

    try:
        # Make a POST request to get the user token
        response = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        data = json.loads(response.stdout)
        user_token = data.get('token', None)
        if user_token:
            return JsonResponse({'token': user_token})
        else:
            print("Token not found in response")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to obtain XAPP Token: {e}")
        print(e.stderr)  # Display error output
        return None
    
def get_paginated_artworks(request):
    collection = db['artworks']

    # Get the page number from the request query parameters
    page_number = int(request.GET.get('page', 1))
    page_size = 10

    # Get the total count of artworks
    total_artworks = collection.count_documents({})

    # Retrieve artworks from MongoDB with pagination
    artworks = list(collection.find({}, artwork_projection).skip((page_number - 1) * page_size).limit(page_size))

    # Create a Paginator instance
    paginator = Paginator(artworks, page_size)

    # Get the current page of artworks
    page_obj = paginator.get_page(page_number)

    # Prepare the response data
    response_data = {
        'count': total_artworks,
        'next': (page_number * page_size) < total_artworks,
        'previous': page_number > 1,
        'results': list(page_obj.object_list)
    }

    return JsonResponse(response_data)

def get_artwork_by_id(request, id):
    collection = db['artworks']

    # Retrieve artworks from MongoDB with pagination
    artwork = collection.find_one({'id': id}, artwork_projection)

    # Prepare the response data
    if(artwork):
        return JsonResponse(artwork)
    else:
        return JsonResponse({'message': f'Could not find any artwork with id: ${id}'})

def get_artwork_by_category(request, category):
    collection = db['artworks']

    # Get the page number from the request query parameters
    page_number = int(request.GET.get('page', 1))
    page_size = 10

    # Get the total count of artworks
    total_artworks = collection.count_documents({'category': category})

    # Retrieve artworks from MongoDB with pagination
    artworks = list(collection.find({'category': category}, artwork_projection).skip((page_number - 1) * page_size).limit(page_size))

    # Create a Paginator instance
    paginator = Paginator(artworks, page_size)

    # Get the current page of artworks
    page_obj = paginator.get_page(page_number)

    # Prepare the response data
    response_data = {
        'count': total_artworks,
        'next': (page_number * page_size) < total_artworks,
        'previous': page_number > 1,
        'results': list(page_obj.object_list)
    }

    return JsonResponse(response_data)

def get_artist_details(session, artwork):
    artists_url = artwork.get('_links', {}).get('artists', {}).get('href', None)
    if artists_url:
        retry_count = 0
        max_retries = 3
        retry_delay = 1  # Initial delay in seconds

        while retry_count < max_retries:
            artists_response = session.get(artists_url)
            if artists_response.status_code == 200:
                artists_data = artists_response.json().get('_embedded', {}).get('artists', [])
                artwork['artists'] = [
                    {
                        'id': artist.get('id'),
                        'name': artist.get('name'),
                        'gender': artist.get('gender', None),
                        'birthday': artist.get('birthday', None),
                        'deathday': artist.get('deathday', None),
                        'nationality': artist.get('nationality', None),
                        'artworks': artist.get('_links', {}).get('artworks', {}).get('href', None),
                        'similar_artists': artist.get('_links', {}).get('similar_artists', {}).get('href', None)
                    }
                    for artist in artists_data
                ]
                break
            else:
                retry_count += 1
                retry_delay *= 2  # Double the delay for the next retry
                print(f"Request failed with status code {artists_response.status_code}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        if retry_count == max_retries:
            print(f"Maximum retries ({max_retries}) exceeded for artists URL: {artists_url}")

def put_paginated_genes(request):
    token_response = get_token(request)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        return JsonResponse({'error': 'Failed to obtain user token'})
    
    session = setup_session()
    session.headers.update({'X-XAPP-Token': user_token})
    
    # API endpoint to get artworks
    url = 'https://api.artsy.net/api/genes'
    # artworks_data = []

    while 1:
        response = session.get(url)
        # print(response)

        responseData = response.json()
        # print(responseData)
        if responseData is not None and responseData:

            client = MongoClient('mongodb+srv://Tejeshu:TejBigData@cluster0.scubujn.mongodb.net/')

            db = client['Final_Project']
            collection = db['genes_paginated']

            collection.insert_one(responseData)

            if 'next' in responseData['_links']:
                next_href = responseData['_links']['next']['href']
                url = next_href
            else:
                break
            # print(next_href)
        else:
            break

def put_genes(request):
    client1 = MongoClient("mongodb+srv://Tejeshu:TejBigData@cluster0.scubujn.mongodb.net/")
    database1 = client1["Final_Project"]
    collection1 = database1["genes_paginated"]

    client2 = MongoClient("mongodb+srv://Tejeshu:TejBigData@cluster0.scubujn.mongodb.net/")
    database2 = client2["Final_Project"]
    collection2 = database2["genes"]

    for document in collection1.find():
        data = document
        for gene in data["_embedded"]["genes"]:
            if gene is not None or not gene:
                collection2.insert_one(gene)

def genes_rows(request):
    spark = SparkSession \
    .builder \
    .appName("genes_rows") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    token_response = get_token(request)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        return JsonResponse({'error': 'Failed to obtain user token'})
    
    session = setup_session()
    session.headers.update({'X-XAPP-Token': user_token})

    client1 = MongoClient("mongodb://localhost:27017/")
    database1 = client1["Final_Project"]
    collection1 = database1["artworks_copy1"]

    document_count = collection1.count_documents({})

    genes_rows = []
    artworks_list = []
    variable = 0
    error1 = 0
    error2 = 0
    error3 = 0

    while variable<document_count:
        for document in collection1.find():
            data = document
            genes_list = []
            self_link = data["_links"]["genes"]["href"]
            artwork_id = data["id"]
            artworks_list.append(artwork_id)
            links_list = []
            if self_link is not None or not self_link:
                response = session.get(self_link)
                try:
                    responseData = response.json()
                except json.decoder.JSONDecodeError:
                    print("JSONDecodeError: Unable to parse response as JSON.(1)")
                    error1 = error1 + 1
                links_list.append(self_link)
                time.sleep(0.05)
            while "next" in responseData["_links"]:
                next_link = responseData["_links"]["next"]["href"]
                response = session.get(next_link)
                try:
                    responseData = response.json()
                    links_list.append(next_link)
                except json.decoder.JSONDecodeError:
                    print("JSONDecodeError: Unable to parse response as JSON.(2)")
                    error2 = error2 + 1
                time.sleep(0.05)
        
            for link in links_list:
                response = session.get(link)
                try:
                    responseData = response.json()
                    if "_embedded" in responseData and "genes" in responseData["_embedded"]:
                        for i in range(len(responseData["_embedded"]["genes"])):
                            if responseData["_embedded"]["genes"][i]["id"]:
                                gene_id = responseData["_embedded"]["genes"][i]["id"]
                                genes_list.append(gene_id)
                                row = [artwork_id, gene_id]
                                genes_rows.append(row)
                        time.sleep(0.05)
                except json.decoder.JSONDecodeError:
                    print("JSONDecodeError: Unable to parse response as JSON.(3)")
                    error3 = error3 + 1
            variable = variable + 1

    schema = StructType([
        StructField("artwork_id", StringType(), True),
        StructField("gene", StringType(), True)
    ])

    rdd = spark.sparkContext.parallelize(genes_rows)

    # columns = ['artwork_id', 'gene']
    row_df = spark.createDataFrame(rdd, schema)

    row_df.write.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.genes_rows')\
    .save()

def artworks_words(request):
    spark = SparkSession \
    .builder \
    .appName("artworks_words") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb+srv://Tejeshu:TejBigData@cluster0.scubujn.mongodb.net/Final_Project.genes')\
    .load()

    descriptions_df = df.select(["id","description"])

    normalized_desc_df = descriptions_df.select(["id",lower(regexp_replace('description', '[^0-9a-zA-Z]+', ' ')).alias('descs')])

    normal_desc_explode = normalized_desc_df.select(["id",explode(split("descs", " ")).alias('words')])

    desc_explode_group = normal_desc_explode.groupby(["id", "words"]).count()

    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

    for word in stop_words:
        genes_words = desc_explode_group.filter(desc_explode_group['words'] != word)

    for word in stop_words:
        genes_words = genes_words.filter(genes_words['words'] != word)

    genes_words = genes_words.where(col("words") != "")

    row_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.genes_rows')\
    .load()

    combined_df = row_df.join(genes_words, row_df.gene == genes_words.id, "left")

    combined_grouped = combined_df.groupBy("artwork_id", "words").agg(F.sum("count").alias("total_count"))

    combined_grouped.write.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb+srv://Tejeshu:TejBigData@cluster0.scubujn.mongodb.net/Final_Project.artworks_words')\
    .save()

def price_data(request):
    spark = SparkSession \
    .builder \
    .appName("price_data") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks')\
    .load()

    min_random = 1000
    max_random = 10000

    df = df.withColumn("price", (rand() * (max_random - min_random) + min_random).cast("int"))
    df = df.select(["id", "price"])

    df.write.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks_prices')\
    .save()

def favourites_data(request):
    spark = SparkSession \
    .builder \
    .appName("favourites_data") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    artworks_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks')\
    .load()

    favourites_df = artworks_df.sample(False, 40/26070)
    favourites_df = favourites_df.select("id")

    favourites_df.write.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.favourites')\
    .save()

def investments_data(request):
    spark = SparkSession \
    .builder \
    .appName("investments_data") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    artworks_prices_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks_prices')\
    .load()

    investments_df = artworks_prices_df.sample(False, 100/26070)

    investments_df.write.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.investments')\
    .save()

def recommended_favourites(request):
    spark = SparkSession \
    .builder \
    .appName("recommended_favourites") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    artworks_words_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks_words')\
    .load()

    favourites_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.favourites')\
    .load()

    artworks_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks')\
    .load()

    favourites_list = [row["id"] for row in favourites_df.collect()]
    favourites_set = set(favourites_list)
    artworks_filtered_df = artworks_df.filter(col("id").isin(favourites_set))

    art_category_list = []

    for row in artworks_filtered_df.collect():
        category = row["category"]
        if category and category not in art_category_list:
            art_category_list.append(row["category"])

    art_medium_list = []

    for row in artworks_filtered_df.collect():
        medium = row["medium"]
        if medium and medium not in art_category_list:
            art_medium_list.append(row["medium"])

    art_category_set = set(art_category_list)
    artworks_category_filtered_df = artworks_df.filter(col("category").isin(art_category_set))
    artworks_category_filtered_df = artworks_category_filtered_df.select("id")

    art_medium_set = set(art_medium_list)
    artworks_medium_filtered_df = artworks_df.filter(col("medium").isin(art_medium_set))
    artworks_medium_filtered_df = artworks_medium_filtered_df.select("id")

    union_df = artworks_category_filtered_df.union(artworks_medium_filtered_df).dropDuplicates()

    favourites_list = [row["id"] for row in favourites_df.collect()]
    favourites_set = set(favourites_list)
    artworks_words_filtered_df = artworks_words_df.filter(col("artwork_id").isin(favourites_set))

    artworks_words_filtered_df_grouped = artworks_words_filtered_df.groupBy("words").agg(F.sum("total_count").alias("count"))
    artworks_words_filtered_df_grouped_sorted = artworks_words_filtered_df_grouped.orderBy(col("count").desc())

    most_word_row = artworks_words_filtered_df_grouped_sorted.first()
    if most_word_row is not None:
        most_word = most_word_row["words"]

    union_words_df = union_df.join(artworks_words_df, union_df.id == artworks_words_df.artwork_id, "left")

    union_words_df = union_words_df.select("artwork_id", "words", "total_count")
    union_words_df_filtered = union_words_df.where(col("words") == most_word)
    union_words_df_filtered_ordered = union_words_df_filtered.orderBy(col("total_count").desc())

    recommended_favourites_list = [row["artwork_id"] for row in union_words_df_filtered_ordered.collect()]
    return recommended_favourites_list

def recommended_investments(request):
    spark = SparkSession \
    .builder \
    .appName("recommended_investments") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    artworks_words_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks_words')\
    .load()

    investments_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.investments')\
    .load()

    artworks_prices_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks_prices')\
    .load()

    artworks_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks')\
    .load()

    average_price = investments_df.select(avg("price")).collect()[0][0]

    investments_list = [row["id"] for row in investments_df.collect()]
    investments_set = set(investments_list)
    artworks_filtered_df = artworks_df.filter(col("id").isin(investments_set))

    art_category_list = []
    for row in artworks_filtered_df.collect():
        category = row["category"]
        if category and category not in art_category_list:
            art_category_list.append(row["category"])

    art_medium_list = []
    for row in artworks_filtered_df.collect():
        medium = row["medium"]
        if medium and medium not in art_category_list:
            art_medium_list.append(row["medium"])

    art_category_set = set(art_category_list)
    artworks_category_filtered_df = artworks_df.filter(col("category").isin(art_category_set))
    artworks_category_filtered_df = artworks_category_filtered_df.select("id")

    art_medium_set = set(art_medium_list)
    artworks_medium_filtered_df = artworks_df.filter(col("medium").isin(art_medium_set))
    artworks_medium_filtered_df = artworks_medium_filtered_df.select("id")

    union_df = artworks_category_filtered_df.union(artworks_medium_filtered_df).dropDuplicates()

    filtered_artworks_prices_df = artworks_prices_df.filter((col("price") >= average_price - 1000) & (col("price") <= average_price + 1000))
    filtered_artworks_prices_df = filtered_artworks_prices_df.withColumnRenamed('id', 'artwork_id')

    categorical_filtered_prices_df = union_df.join(filtered_artworks_prices_df, union_df['id'] == filtered_artworks_prices_df['artwork_id'], 'inner')

    investments_list = [row["id"] for row in investments_df.collect()]
    investments_set = set(investments_list)
    artworks_words_filtered_df = artworks_words_df.filter(col("artwork_id").isin(investments_set))

    artworks_words_filtered_df_grouped = artworks_words_filtered_df.groupBy("words").agg(F.sum("total_count").alias("count"))
    artworks_words_filtered_df_grouped_sorted = artworks_words_filtered_df_grouped.orderBy(col("count").desc())

    most_word_row = artworks_words_filtered_df_grouped_sorted.first()
    if most_word_row is not None:
        most_word = most_word_row["words"]

    categorical_filtered_words_df = categorical_filtered_prices_df.join(artworks_words_df, categorical_filtered_prices_df.id == artworks_words_df.artwork_id, "left")
    categorical_filtered_words_df = categorical_filtered_words_df.drop("artwork_id")
    categorical_filtered_words_df = categorical_filtered_words_df.select("id", "price", "words", "total_count")
    investments_filtered_df = categorical_filtered_words_df.where(col("words") == most_word)
    investments_filtered_df_ordered = investments_filtered_df.orderBy(col("total_count").desc())

    recommended_investments_list = [row["id"] for row in investments_filtered_df_ordered.collect()]
    return recommended_investments_list

def get_artworks_by_keyword(request, keyword):
    spark = SparkSession \
    .builder \
    .appName("keywords_search") \
    .master('local')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .config('spark.driver.memory','32g')\
    .getOrCreate()

    artworks_words_df = spark.read.format('com.mongodb.spark.sql.DefaultSource')\
    .option('uri','mongodb://localhost:27017/Final_Project.artworks_words')\
    .load()

    words = keyword.split()
    words = [word.lower() for word in words]
    keywords_list = words
    keywords_set = set(keywords_list)

    filtered_arts = artworks_words_df.where(col("words").isin(keywords_set))
    filtered_arts_grouped = filtered_arts.groupBy("artwork_id").agg(F.sum("total_count").alias("count"))
    filtered_arts_grouped_sorted = filtered_arts_grouped.orderBy(col("count").desc())

    similar_arts_list = [row["artwork_id"] for row in filtered_arts_grouped_sorted.limit(20).collect()]

    return similar_arts_list

def put_artworks(request):
    # Get the user token by calling the get_token function
    token_response = get_token(request)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        return JsonResponse({'error': 'Failed to obtain user token'})
    
    session = setup_session()
    session.headers.update({'X-XAPP-Token': user_token})
    
    # API endpoint to get artworks
    artworks_url = 'https://api.artsy.net/api/artworks'
    artworks_data = []

    # Loop through paginated results
    while artworks_url:
        retry_count = 0
        max_retries = 3
        retry_delay = 1  # Initial delay in seconds

        while retry_count < max_retries:
            response = session.get(artworks_url)
            if response.status_code == 200:
                break
            else:
                retry_count += 1
                retry_delay *= 2  # Double the delay for the next retry
                print(f"Request failed with status code {response.status_code}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        if retry_count == max_retries:
            print(f"Maximum retries ({max_retries}) exceeded. Skipping to the next page.")
            next_page = None
        else:
            data = response.json()

            # Extract artworks from the current page
            artworks = data.get('_embedded', {}).get('artworks', [])
            for artwork in artworks:
                get_artist_details(session, artwork)
            
            artworks_data.extend(artworks)

            # Get the next page URL
            next_page = data.get('_links', {}).get('next', {}).get('href', None)

        artworks_url = next_page

    # Store artworks in MongoDB
    collection = db['artworks']
    try:
        result = collection.insert_many(artworks_data)
        return JsonResponse({'message': f'{len(result.inserted_ids)} artworks added to MongoDB'})
    except Exception as e:
        return JsonResponse({'message': 'Failed to insert records to the mongodb', 'error': str(e)}, status = 500)

def get_artists(request):
    collection = db['artworks']

    # Query to get a list of unique artists with names and IDs
    pipeline = [
        {"$unwind": "$artists"},
        {"$group": {"_id": {"name": "$artists.name", "id": "$artists.id"}, "count": {"$sum": 1}}},
        {"$project": {"artist_name": "$_id.name", "artist_id": "$_id.id", "_id": 0}}
    ]

    result = collection.aggregate(pipeline)

    # Store unique artists in a list
    unique_artists = []
    for artist in result:
        unique_artists.append({"name": artist["artist_name"], "id": artist["artist_id"]})

    return JsonResponse(unique_artists, safe=False)

def get_categories(request):
    collection = db['artworks']
    result = collection.distinct('category')

    return JsonResponse(result, safe=False)

def get_artworks_by_artist(request, artist_id):
    collection = db['artworks']

    page_number = int(request.GET.get('page', 1))
    page_size = 10

    total_artworks = collection.count_documents({"artists.id": artist_id})

    artworks = list(collection.find({"artists.id": artist_id}, artwork_projection).skip((page_number - 1) * page_size).limit(page_size))

    paginator = Paginator(artworks, page_size)
    page_obj = paginator.get_page(page_number)

    response_data = {
        'count': total_artworks,
        'next': (page_number * page_size) < total_artworks,
        'previous': page_number > 1,
        'results': list(page_obj.object_list)
    }

    return JsonResponse(response_data)

def get_artworks_by_period(request, period):
    collection = db['artworks']

    # Get the page number from the request query parameters
    page_number = int(request.GET.get('page', 1))
    page_size = 10

    start_date, end_date = map(str.strip, period.split('-'))
    query = {"date": {
        "$gte": start_date,
        "$lte": end_date
    }}
    # Get the total count of artworks
    total_artworks = collection.count_documents(query)

    # Retrieve artworks from MongoDB with pagination
    artworks = list(collection.find(query, artwork_projection).skip((page_number - 1) * page_size).limit(page_size))

    # Create a Paginator instance
    paginator = Paginator(artworks, page_size)

    # Get the current page of artworks
    page_obj = paginator.get_page(page_number)

    # Prepare the response data
    response_data = {
        'count': total_artworks,
        'next': (page_number * page_size) < total_artworks,
        'previous': page_number > 1,
        'results': list(page_obj.object_list)
    }

    return JsonResponse(response_data)