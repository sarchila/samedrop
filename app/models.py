from app import db
from app.utils import create_hash, to_mgdl


class Meter(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    display_name = db.Column(db.String(60))
    glucose_tests = db.relationship('GlucoseTest', backref='meter')

    def __init__(self, display_name):
        self.display_name = display_name

    def as_dict(self):
        return {'display_name': self.display_name}

    @classmethod
    def get_all(cls):
        return [meter.as_dict() for meter in cls.query.all()]


class GlucoseTest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    reading_mgdl = db.Column(db.Integer, nullable=False)
    strip_lot = db.Column(db.Integer)
    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'), nullable=False)
    samedrop_id = db.Column(db.Integer, db.ForeignKey('samedrop.id'), nullable=False)

    def __init__(self, reading_mgdl, strip_lot, meter, samedrop):
        self.reading_mgdl = reading_mgdl
        self.strip_lot = strip_lot
        self.meter = meter
        self.samedrop = samedrop

    def as_dict(self):
        return {
            'meter': self.meter.display_name,
            'reading_mgdl': self.reading_mgdl,
            'strip_lot': self.strip_lot
        }


class Samedrop(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    patient_hashed_id = db.Column(db.String(64))
    test_date = db.Column(db.Date, nullable=False)
    glucose_tests = db.relationship('GlucoseTest', backref='samedrop')

    def __init__(self, email, test_date, glucose_tests):
        self.patient_hashed_id = create_hash(email) if email else None
        self.test_date = test_date

        for glucose_test in glucose_tests:
            meter = Meter.query.filter(Meter.display_name == glucose_test['meter']).first()

            if meter is None:
                meter = Meter(glucose_test['meter'])
                db.session.add(meter)

            db.session.add(GlucoseTest(
                to_mgdl(glucose_test['reading'], glucose_test['units']),
                glucose_test['strip_lot'] if glucose_test['strip_lot'] else None,
                meter,
                self
            ))

    def as_dict(self):
        return {
            'id': self.id,
            'patient_hashed_id': self.patient_hashed_id,
            'test_date': self.test_date.strftime('%Y-%m-%d'),
            'glucose_tests': [test.as_dict() for test in self.glucose_tests]
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        return [samedrop.as_dict() for samedrop in cls.query.all()]
