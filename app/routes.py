#!flask/bin/python
from flask import jsonify, request, abort, make_response, render_template
from app import app, models


#############
# MAIN PAGE #
#############

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html',
                           meters=models.Meter.get_all())

##############
# API ROUTES #
##############


@app.route('/api/samedrops', methods=['GET'])
def get_samedrops():
    samedrops = models.Samedrop.get_all()
    return jsonify({
        'length': len(samedrops),
        'samedrops': samedrops
    })


@app.route('/api/samedrops', methods=['POST'])
def create_samedrop():
    if not request.json or not 'test_date' in request.json or len(request.json['glucose_tests']) == 0:
        abort(400)

    for glucose_test in request.json['glucose_tests']:
        if glucose_test['meter'] == "Select meter" or not glucose_test['reading']:
            abort(400)

    samedrop = models.Samedrop(
        request.json['email'],
        request.json['test_date'],
        request.json['glucose_tests']
    )

    samedrop.save()

    return make_response(jsonify(samedrop.as_dict()), 201)


@app.route('/api/samedrops/<int:samedrop_id>', methods=['GET'])
def get_samedrop(samedrop_id):
    samedrop = models.Samedrop.query.get(samedrop_id)
    if samedrop is None:
        abort(404)
    return jsonify(samedrop.as_dict())


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)
