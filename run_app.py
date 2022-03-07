from app import create_app

app = create_app("testing")

if __name__ == "__main__":
    app.run(host='localhost', port=8080)
