import flask

slash_bp = flask.Blueprint("slash", "slash")


@slash_bp.route('/', methods=['GET'])
def slash():
    return """<!DOCTYPE html>
            <html>
            <body>
            
            <h1>JobsScheduler</h1>
            
            <a href="/api/swagger">Swagger API description</a>
            
            </body>
            </html>"""