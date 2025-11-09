from routes.maps import maps_bp

def register_maps(app):
    app.register_blueprint(maps_bp, url_prefix="/api/maps")
