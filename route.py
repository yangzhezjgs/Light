class Route:
    def __init__(self, app):
        self.app = app
    def __call__(self, url, **options):
        if 'methods' not in options:
            options['methods'] = ['GET']

        def decorator(f):
            self.app.add_url_rule(url, f, 'route',**options)
            return f

        return decorator
