from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
import pandas as pd

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Trips(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(32))
    origin_coord = db.Column(db.String(256))
    destination_coord = db.Column(db.String(256))
    datetime = db.Column(db.String(128))
    datasource = db.Column(db.String(64))

    def __init__(self, region, origin_coord, destination_coord, datetime, datasource):
        self.region = region
        self.origin_coord = origin_coord
        self.destination_coord = destination_coord
        self.datetime = datetime
        self.datasource = datasource



class TripsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'region', 'origin_coord', 'destination_coord', 'datetime', 'date', 'datasource')

trips_schema = TripsSchema()
trips_schema = TripsSchema(many=True)

class UserManager(Resource):
    @staticmethod
    def get():
        try: id = request.args['id']
        except Exception as _: id = None

        if not id:
            users = Trips.query.all()
            return jsonify(users_schema.dump(users))
        id = Trips.query.get(id)
        return jsonify(user_schema.dump(id))

    @staticmethod
    def post():
        uploaded_file = request.files['file']
        col_names = ['region', 'origin_coord', 'destination_coord', 'datetime', 'datasource']
        csvData = pd.read_csv(uploaded_file, names=col_names, header=None, skiprows=1)
        for i, row in csvData.iterrows():
            region = row['region']
            origin_coord = row['origin_coord']
            destination_coord = row['destination_coord']
            datetime = row['datetime']
            datasource = row['datasource']

            user = Trips(region, origin_coord, destination_coord, datetime, datasource)
            db.session.add(user)
            db.session.commit()

        return jsonify({
            'Message': f'{len(csvData.index)} rows from {uploaded_file} where inserted into database.'
        })


api.add_resource(UserManager, '/api/trips')

if __name__ == '__main__':
    app.run(debug=True)