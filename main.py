from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import get_connection

app = FastAPI(title="Smart Logistics API")


@app.get("/")
def serve_frontend():
    return FileResponse("index_11.html")


@app.get("/cities")
def get_cities():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CITY")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


@app.get("/routes")
def get_routes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            Route_ID,
            From_City,
            To_City,
            Distance,
            Traffic_Multiplier,
            ROUND(Distance * Traffic_Multiplier, 2) AS Effective_KM,
            CASE Traffic_Multiplier
                WHEN 1.0 THEN 'clear'
                WHEN 1.5 THEN 'moderate'
                WHEN 2.2 THEN 'heavy'
                ELSE 'unknown'
            END AS Traffic_Level
        FROM ROUTE
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


@app.get("/routes/graph")
def get_adjacency_graph():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            From_City, To_City,
            Distance,
            Traffic_Multiplier,
            ROUND(Distance * Traffic_Multiplier, 2) AS Effective_KM
        FROM ROUTE
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    graph = {}
    for r in rows:
        for src, dst in [(r["From_City"], r["To_City"]),
                         (r["To_City"],   r["From_City"])]:
            if src not in graph:
                graph[src] = []
            graph[src].append({
                "to":           dst,
                "distance":     float(r["Distance"]),
                "multiplier":   float(r["Traffic_Multiplier"]),
                "effective_km": float(r["Effective_KM"])
            })
    return graph


@app.get("/api/cities")
def get_cities_for_map():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT City_Name, State FROM CITY")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    result = []
    for i, row in enumerate(rows):
        result.append({
            "id":     i,
            "name":   row["City_Name"],
            "isBase": row["City_Name"] == "Pune Delivery Center"
        })
    return result


@app.get("/api/roads")
def get_roads_for_map():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            From_City, To_City,
            Distance,
            Traffic_Multiplier,
            CASE Traffic_Multiplier
                WHEN 1.0 THEN 'clear'
                WHEN 1.5 THEN 'moderate'
                WHEN 2.2 THEN 'heavy'
                ELSE 'clear'
            END AS Traffic_Level
        FROM ROUTE
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

