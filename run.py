import yaml
from mutants import app

config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
app.run(host=config['app_host'], port=config['app_port'], debug=config['app_debug'])

