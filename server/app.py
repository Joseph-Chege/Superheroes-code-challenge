#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict(rules=('-hero_powers',)) for hero in heroes], 200
    
    def post(self):
        data = request.get_json()
        hero = Hero(name=data['name'], super_name=data['super_name'])
        db.session.add(hero)
        db.session.commit()
        return hero.to_dict(), 201
    

class HeroesById(Resource):
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if not hero:
            return {"error": "Hero not found"}, 404
        return hero.to_dict(rules=('-hero_powers.hero',))
    
    def patch(self, id):
        data = request.get_json()
        hero = Hero.query.get(id)
        if not hero:
            return {"error": "Hero not found"}, 404
        hero.name = data.get('name', hero.name)
        hero.super_name = data.get('super_name', hero.super_name)
        db.session.commit()
        return hero.to_dict()
    
    def delete(self, id):
        hero = Hero.query.get(id)
        if not hero:
            return {"error": "Hero not found"}, 404
        db.session.delete(hero)
        db.session.commit()
        return {"message": "Hero deleted"}, 200
    

class HeroPowers(Resource):
    def get(self, hero_id):
        hero = Hero.query.get(hero_id)
        if not hero:
            return {"error": "Hero not found"}, 404
        return [power.to_dict() for power in hero.powers]
    
    def post(self, hero_id):
        data = request.get_json()
        hero = Hero.query.get(hero_id)
        if not hero:
            return {"error": "Hero not found"}, 404
        power = Power.query.get(data['power_id'])
        if not power:
            return {"error": "Power not found"}, 404
        
        if data['strength'] not in ['Strong', 'Weak', 'Average']:
            return jsonify({'errors': ['validation errors']}), 400

        hero_power = HeroPower(strength=data['strength'], hero=hero, power=power)
        db.session.add(hero_power)
        db.session.commit()
        return jsonify(hero_power.to_dict(), 201)
    

class HeroPowersById(Resource):
    def get(self, hero_id, power_id):
        hero = Hero.query.filter_by(hero_id=hero_id).first()
        if not hero:
            return {"error": "Hero not found"}, 404
        power = Power.query.filter_by(power_id=power_id).first()
        if not power:
            return {"error": "Power not found"}, 404
        hero_power = HeroPower.query.filter_by(hero_id=hero_id, power_id=power_id).first()
        if not hero_power:
            return {"error": "Hero power not found"}, 404
        return hero_power.to_dict()
    
    def post(self, hero_id, power_id):
        data = request.get_json()
        hero_power = HeroPower.query.filter_by(hero_id=hero_id, power_id=power_id).first()
        if not hero_power:
            return {"error": "Hero power not found"}, 404
        hero_power.strength = data.get('strength', hero_power.strength)
        db.session.commit()
        return hero_power.to_dict()
    
    

    def delete(self, hero_id, power_id):
        hero_power = HeroPower.query.filter_by(hero_id=hero_id, power_id=power_id).first()
        if not hero_power:
            return {"error": "Hero power not found"}, 404
        db.session.delete(hero_power)
        db.session.commit()
        return {"error": "Hero power deleted"}
    
class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict(rules=('-hero_powers',)) for power in powers]
    
    def patch(self):
        data = request.get_json()
        power = Power(name=data['name'], description=data['description'])
        db.session.add(power)
        db.session.commit()
        
        return power.to_dict(), 201
    

class PowersById(Resource):
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if not power:
            return {"error": "Power not found"}, 404
        return power.to_dict(rules=('-hero_powers',))
    
    def patch(self, id):
        data = request.get_json()
        power = Power.query.filter_by(id=id).first()
        if not power:
            return {"error": "Power not found"}, 404
        power.name = data.get('name', power.name)
        power.description = data.get('description', power.description)

    
        if len(power.description) < 20:
            return jsonify({'errors': ['validation errors']}), 404
        db.session.commit()
        return jsonify(power.to_dict())

    def delete(self, id):
        power = Power.query.filter_by(id=id).first()
        if not power:
            return {"error": "Power not found"}, 404
        db.session.delete(power)
        db.session.commit()
        return {"message": "Power deleted"}, 200
    


api = Api(app)

api.add_resource(Heroes, '/heroes')
api.add_resource(HeroesById, '/heroes/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')
api.add_resource(HeroPowersById, '/heroes/<int:hero_id>/powers/<int:power_id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowersById, '/powers/<int:id>')



if __name__ == '__main__':
    app.run(port=5555, debug=True)
