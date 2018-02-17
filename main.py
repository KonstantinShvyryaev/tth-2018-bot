import os
from app import app, bot
import view

### Main ###
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))