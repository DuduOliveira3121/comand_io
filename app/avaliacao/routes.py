from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.avaliacao import Avaliacao
from app.models.pedido import Pedido
from sqlalchemy import func

bp_avaliacoes = Blueprint('avaliacoes', __name__)

@bp_avaliacoes.route('/avaliacoes/', methods=['POST'])
def criar_avaliacao():
    dados = request.get_json()
    pedido_id = dados.get('pedido_id')
    nota = dados.get('nota')
    comentario = dados.get('comentario', '')

    if not pedido_id or not nota:
        return jsonify({'erro': 'pedido_id e nota são obrigatórios'}), 400

    try:
        nota = int(nota)
        if nota < 1 or nota > 5:
            return jsonify({'erro': 'A nota deve estar entre 1 e 5'}), 400
    except ValueError:
        return jsonify({'erro': 'A nota deve ser um número inteiro'}), 400

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({'erro': 'Pedido não encontrado'}), 404
        
    if pedido.status != 'fechado':
        return jsonify({'erro': 'A avaliação só pode ser feita para pedidos fechados'}), 403

    nova_avaliacao = Avaliacao(
        pedido_id=pedido_id,
        nota=nota,
        comentario=comentario
    )
    
    db.session.add(nova_avaliacao)
    db.session.commit()

    return jsonify({'mensagem': 'Avaliação registada com sucesso!'}), 201


@bp_avaliacoes.route('/avaliacoes/', methods=['GET'])
def listar_avaliacoes():
    media = db.session.query(func.avg(Avaliacao.nota)).scalar()
    media_geral = round(media, 2) if media else 0.0

    avaliacoes = Avaliacao.query.order_by(Avaliacao.criado_em.desc()).all()
    
    lista_avaliacoes = [{
        'id': av.id,
        'pedido_id': av.pedido_id,
        'nota': av.nota,
        'comentario': av.comentario,
        'criado_em': av.criado_em.strftime('%d/%m/%Y %H:%M:%S')
    } for av in avaliacoes]

    return jsonify({
        'media_geral': media_geral,
        'avaliacoes': lista_avaliacoes
    }), 200