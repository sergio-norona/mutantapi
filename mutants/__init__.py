from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
import yaml
import platform
import socket
import requests

application = app = Flask(__name__)
db_config = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+db_config['mysql_user']+':'+db_config['mysql_password']+'@'+db_config['mysql_host']+'/'+db_config['mysql_database']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


api = Api(app)
db = SQLAlchemy(app)

class Dna(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sequence = db.Column(db.Text, primary_key = False, nullable=False)
    ismutant = db.Column(db.Integer, primary_key = False, nullable=False)

    def __repr__(self):
        return '<id %r>' % self.id

@app.route('/')
def hello_world():
    title = 'Hello, World! this is some service info:'
    new_line = '<br>'
    sql_hostname = '' #'Sql Hostname: ' + str(db_config['mysql_host'])
    platform_info = 'Platform Info: ' + platform.platform()
    total_dna_sequences = 'Total Database Dna Saved: ' + str(Dna.query.count())

    return new_line.join([title, sql_hostname, platform_info, total_dna_sequences])

class Mutant(Resource):
    def post(self):
        content = request.get_json(silent=True)
        matrix = Matrix()
        dna_matrix = matrix.build_matrix_from_dna_sample(content['dna'])
        
        dna = DnaSequence()
        is_mutant = dna.is_mutant(dna_matrix)

        #update stats
        #if there is complex statistics, it should be in another database with an associated microservice 
        #implement dna.update_stats(is_mutant) and set updated_stats with boolean result

        try:
            dna.add_to_database(str(content), is_mutant)
            saved_to_database = True
            updated_stats = True
        except:
            saved_to_database = False
            updated_stats = False

        if is_mutant:
            status_code = 200
        else:
            status_code = 403

        return {'isMutant':is_mutant, 'updatedStats':updated_stats, 'savedToDatabase':saved_to_database}, status_code

class Dummy(Resource):
    def get(self):
        return {'message': 'ok'}, 200

class DnaSequence:
    sequence = []

    def is_mutant(self, dna_matrix):
        matrix = Matrix()
        length = 4 # sacar a configuración

        for y in range(0, len(dna_matrix)):
            for x in range(0, len(dna_matrix[y])):
                char = dna_matrix[y][x]

                result_up_right = matrix.select_up_right_diagonal_from_matrix(length, dna_matrix, x, y)
                if result_up_right is not False and result_up_right.count(char) == length:
                    return True

                result_down_right = matrix.select_down_right_diagonal_from_matrix(length, dna_matrix, x, y)
                if result_down_right is not False and  result_down_right.count(char) == length:                    
                    return True

                result_horizontal_right = matrix.select_horizontal_to_right_from_matrix(length, dna_matrix, x, y)
                if result_horizontal_right is not False and  result_horizontal_right.count(char) == length:
                    return True

                result_vertical_down = matrix.select_vertical_to_down_from_matrix(length, dna_matrix, x, y)
                if result_vertical_down is not False and  result_vertical_down.count(char) == length:
                    return True

        return False

    def add_to_database(self, sequence, is_mutant):
    	dna = Dna()
    	dna.sequence = sequence
    	dna.ismutant = is_mutant
    	db.session.add(dna)
    	db.session.commit()
    	return True

    #def update_stats(self, stats):
    #	response = requests.put(f'http://microservicios.stats.com/stats')
    #	return response.status_code

class Matrix:

    def build_matrix_from_dna_sample(self, dna_sample):
        matrix = []
        for x in range(0, len(dna_sample)):
            result = list(dna_sample[x])
            matrix.append(result)
        return matrix

    def select_up_right_diagonal_from_matrix(self, select_length, matrix, x, y):
        try:
            result = ''
            positions = []
            for i in range(0, select_length):
                positions.append([y-i, x+i])

            for n in range(0, len(positions)):
                if positions[n][0] < 0 or positions[n][1] < 0:
                    result = False
                    break
                result = result + matrix[positions[n][0]][positions[n][1]]

        except:
            result = False

        return result

    def select_down_right_diagonal_from_matrix(self, select_length, matrix, x, y):
        try:
            result = ''
            positions = []
            for i in range(0, select_length):
                positions.append([y+i, x+i])

            for n in range(0, len(positions)):
                result = result + matrix[positions[n][0]][positions[n][1]]

        except:
            result = False

        return result

    def select_horizontal_to_right_from_matrix(self, select_length, matrix, x, y):
        try:
            result = ''
            positions = []
            for i in range(0, select_length):
                positions.append([y, x+i]) 

            for n in range(0, len(positions)):
                result = result + matrix[positions[n][0]][positions[n][1]]

        except:
            result = False

        return result

    def select_vertical_to_down_from_matrix(self, select_length, matrix, x, y):
        try:
            result = ''
            positions = []
            for i in range(0, select_length):
                positions.append([y+i, x])

            for n in range(0, len(positions)):
                result = result + matrix[positions[n][0]][positions[n][1]]

        except:
            result = False

        return result


api.add_resource(Mutant, '/mutant')
api.add_resource(Dummy, '/dummy')



