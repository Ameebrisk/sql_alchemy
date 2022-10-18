import json
import psycopg2
from flask import Flask, request, jsonify

from db import *
from users import Users
from organizations import Organizations

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://Amee@localhost:5432/alchemy"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app, db)

def create_all():
  with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("All done!")

@app.route('/user/add', methods=['POST'] )
def user_add():
  post_data = request.json
  if not post_data:
    post_data = request.post

  first_name = post_data.get('first_name')
  last_name = post_data.get('last_name')
  email = post_data.get('email')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  org_id = post_data.get('org_id')
  active = post_data.get('active')

  add_user(first_name, last_name, email, phone, city, state, org_id, active)

  return jsonify("User created"), 201

  

def add_user(first_name, last_name, email, phone, city, state, org_id, active): 
  new_user = Users(first_name, last_name, email, phone, city, state, org_id, active)
  
  db.session.add(new_user)
  db.session.commit()

@app.route('/user_by_id/get/<user_id>', methods=['GET'] )
def get_user_by_id(user_id):
  user = db.session.query(Users).filter(Users.user_id == user_id).first()
  if user:
    new_user = {
      'user_id': user.user_id,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email,
      'phone': user.phone,
      'city': user.city,
      'state': user.state,
      'organization': {
        'org_id': user.org.org_id,
        'name': user.org.name,
        'phone': user.org.phone,
        'city': user.org.city,
        'state': user.org.state
      },
      'active': user.active
    }

  return jsonify(new_user), 200

@app.route('/org/add', methods=['POST'] )
def org_add():
    post_data = request.json
    if not post_data:
        post_data = request.form
    name = post_data.get('name')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    active = post_data.get('active')

    add_org(name, phone, city, state, active)

    return jsonify("Org created"), 201

def add_org(name, phone, city, state, active):
  new_org = Organizations(name, phone, city, state, active)
  db.session.add(new_org)
  db.session.commit()


@app.route('/users/get', methods=['GET'] )
def get_all_active_users():
  users = db.session.query(Users).filter(Users.active == True).all()
  users_list = []

  for user in users:
    new_user = {
      'user_id': user.user_id,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email,
      'phone': user.phone,
      'city': user.city,
      'state': user.state,
      'organization': {
        'org_id': user.org.org_id,
        'name': user.org.name,
        'phone': user.org.phone,
        'city': user.org.city,
        'state': user.org.state
      },
      'active': user.active
    }

    users_list.append(new_user)

  return jsonify(users_list), 200


@app.route('/orgs/get', methods=['GET'] )
def get_all_active_orgs():
  orgs = db.session.query(Organizations).filter(Organizations.active == True).all()
  orgs_list = []

  for org in orgs:
    new_org = {
      
      'org_id': org.org_id,
      'name': org.name,
      'phone': org.phone,
      'city': org.city,
      'state': org.state,
      'active': org.active
    }

    orgs_list.append(new_org)

  return jsonify(orgs_list), 200
  

@app.route('/org/update/<org_id>', methods=['POST', 'PUT'])
def org_update(org_id):
  organization = db.session.query(Organizations).filter(Organizations.org_id==org_id).first()

  if not organization: 
    return jsonify(f'Org with id {org_id} not found'), 404

  post_data = request.json

  if not post_data:
    post_data = request.form

  if post_data.get('name'):
    organization.name = post_data.get('name')
  if post_data.get('phone'):
    organization.phone = post_data.get('phone')
  if post_data.get('city'):
    organization.city = post_data.get('city')
  if post_data.get('state'):
    organization.state = post_data.get('state')
  if 'active' in post_data:
    organization.active = post_data.get('active')

  db.session.commit()

  return jsonify('Organization"s values updated'), 200

@app.route('/org/activate/<org_id>', methods=['GET'] )
def org_activate(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  results.active=True
  db.session.commit()
  return jsonify('Organization Activated'), 200

@app.route('/user/activate/<user_id>', methods=['GET'] )
def user_activate(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  results.active=True
  db.session.commit()
  return jsonify('User Activated'), 200

@app.route('/org/deactivate/<org_id>', methods=['GET'] )
def org_deactivate(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  results.active=False
  db.session.commit()
  return jsonify('Organization Deactivated'), 200

@app.route('/user/activate/<user_id>', methods=['GET'] )
def user_deactivate(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  results.active=False
  db.session.commit()
  return jsonify('User Deactivated'), 200

@app.route('/org/delete/<org_id>', methods=['DELETE'] )
def org_delete(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  db.session.delete(results)
  db.session.commit()
  return jsonify('Organization Deleted'), 200

@app.route('/user/delete/<user_id>', methods=['DELETE'] )
def user_delete(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  db.session.delete(results)
  db.session.commit()
  return jsonify('User Deleted'), 200


if __name__ == '__main__':
  create_all()
  app.run(host='0.0.0.0', port="8089")