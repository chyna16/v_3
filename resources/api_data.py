from flask import jsonify, Blueprint
from flask.ext.restful import Resource, Api
import os
import settings
import repo_manager
import data_manager

class FolderList(Resource):
	def get(self):
		dir_list = repo_manager.get_dir_list(settings.csv_dir)
		return jsonify({'csv_files': dir_list})


class CSVData(Resource):
	def get(self, analysis, repo_name, from_date, to_date):
		repo_details = repo_name + "_" + from_date + "_" + to_date
		folder = os.path.join(settings.csv_dir, repo_details)
		if analysis == 'cloud':
			data, keys = data_manager.get_word_frequency(folder,
				analysis + "_" + repo_details + ".log")
		else:
			data, keys = data_manager.parse_csv(folder,
				analysis + "_" + repo_name + ".csv")
		if data == []:
			return jsonify({'null': 'data is not available for this query'})
		else:
			return jsonify({'repo': repo_name,
							'from_date': from_date,
							'to_date': to_date,
							'headers': keys,
							'data': data})


csv_api = Blueprint('resources.api_data', __name__)
api = Api(csv_api)
api.add_resource(
	FolderList,
	'/api/v1/data',
	endpoint='data'
)
api.add_resource(
	CSVData,
	'/api/v1/data/<string:repo_name>&<string:analysis>&<string:from_date>&<string:to_date>'
)