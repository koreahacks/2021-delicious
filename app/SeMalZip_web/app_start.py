from SeMalZip_web import app, db


if __name__ == "__main__":
    app.debug = True
    db.create_all()
    app.run(host="127.0.0.1")