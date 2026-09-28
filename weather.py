import requests

API_KEY="ecdf5ca962760d488499894d1a34151f"

def get_weather(lat,lon):

    url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response=requests.get(url)

    data=response.json()

    return {
        "temperature":data["main"]["temp"],
        "humidity":data["main"]["humidity"]
    }