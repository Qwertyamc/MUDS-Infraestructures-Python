from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import psycopg

app = Flask(__name__)
CORS(app)

connection_params = {
    "host": "localhost",
    "port": 5433,
    "dbname": "postgres", 
    "user": "admin",
    "password": "admin",
    "client_encoding":'WIN1252'
}

def extractInfo(data):
    return [{
        "id":anime["mal_id"],
        "title":anime["titles"][0]["title"],
        "image":anime["images"]["jpg"]["image_url"],
        "url":anime["url"]
    } for anime in data]

@app.route('/api/getAnimes', methods=['GET'])
def getAnimes():
    data = requests.get("https://api.jikan.moe/v4/anime?limit=6&order_by=score&sort=desc").json()
    return extractInfo(data["data"])

@app.route('/api/searchAnimes', methods=['GET'])
def searchAnimes():
    search = request.args.get('search', 'zero')
    data = requests.get(f"https://api.jikan.moe/v4/anime?limit=12&order_by=score&sort=desc&q={search}").json()
    return extractInfo(data["data"])

@app.route('/api/getFavoritesList', methods=['GET'])
def getFavoritesList():
    data = {'favorites':[]}
    print("OUTSIDE!")
    try:
        print("INSIDE!")
        connection = psycopg.connect(**connection_params)
        print("Connection successful!")

        cursor = connection.cursor()

        cursor.execute("""
            SELECT ID
            FROM favorites
        """)
        tables = cursor.fetchall()

        data = {'favorites':[]}
        for table in tables:
            data["favorites"].append(table[0])

    except psycopg.OperationalError as e:
        print(f"Could not connect to the database: {e}")
    except psycopg.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(e)

    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("Connection closed.")
    return data

@app.route('/api/getFavorites', methods=['GET'])
def getFavorites():
    favorites = getFavoritesList()
    favorites = favorites["favorites"]

    data = []
    for index in favorites:
        d = requests.get(f"https://api.jikan.moe/v4/anime/{index}").json()
        data.append(d["data"])
    return extractInfo(data)



@app.route('/api/addFavorite', methods=['POST'])
def addFavorite():
    data = request.get_json()
    try:
        connection = psycopg.connect(**connection_params)
        print("Connection successful!")

        cursor = connection.cursor()

        cursor.execute(f"""
            INSERT INTO favorites
            VALUES ({data['id']});
        """)

        connection.commit()

    except psycopg.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        return 'False'
    except psycopg.Error as e:
        print(f"Database error: {e}")
        return 'False'

    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("Connection closed.")
    return 'True'
    
@app.route('/api/removeFavorite', methods=['POST'])
def removeFavorite():
    data = request.get_json()
    try:
        connection = psycopg.connect(**connection_params)
        print("Connection successful!")

        cursor = connection.cursor()

        cursor.execute(f"""
            DELETE FROM favorites
            WHERE ID = {data['id']};
        """)
        
        connection.commit()

    except psycopg.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        return 'False'
    except psycopg.Error as e:
        print(f"Database error: {e}")
        return 'False'

    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("Connection closed.")
    return 'True'

app.run(host='0.0.0.0', port=5000)