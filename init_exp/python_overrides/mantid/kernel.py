import js

class logger():
    
    @staticmethod
    def warning(message):
        js.console.log(f'Warning: {message}')
