from controllers.user_controller import register_user_routes
from controllers.artist_controller import register_artist_routes
from controllers.music_controller import register_music_routes

def register_all_routes(route):
    """Register all routes with the router"""
    register_user_routes(route)
    register_artist_routes(route)
    register_music_routes(route)