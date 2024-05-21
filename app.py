from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pagamentos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Pagamento {self.pedido_id} {self.status}>'

# Cria o banco de dados e as tabelas
@app.before_first_request
def create_tables():
    db.create_all()

class PagamentoResource(Resource):
    def get(self, pedido_id):
        pagamento = Pagamento.query.filter_by(pedido_id=pedido_id).first()
        if pagamento:
            return jsonify({'pedido_id': pagamento.pedido_id, 'status': pagamento.status})
        return {'message': 'Pagamento não encontrado'}, 404

    def post(self):
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        status = data.get('status', 'Pendente')

        if not pedido_id:
            return {'message': 'Pedido ID é obrigatório'}, 400

        pagamento_existente = Pagamento.query.filter_by(pedido_id=pedido_id).first()
        if pagamento_existente:
            return {'message': 'Pagamento já registrado para este pedido'}, 400

        novo_pagamento = Pagamento(pedido_id=pedido_id, status=status)
        db.session.add(novo_pagamento)
        db.session.commit()

        return {'message': 'Pagamento registrado com sucesso', 'pedido_id': novo_pagamento.pedido_id}, 201

api.add_resource(PagamentoResource, '/pagamentos', '/pagamentos/<int:pedido_id>')

if __name__ == '__main__':
    app.run(debug=True)