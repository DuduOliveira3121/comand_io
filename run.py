from app import create_app
from app.extensions import db
from app.models import mesa, pedido, produto, item_pedido
from app.models.mesa import Mesa
from app.models.produto import Produto

def seed_initial_data():
    """Popula o banco com dados iniciais se estiver vazio"""
    try:
        # Verificar se já tem mesas
        if Mesa.query.count() == 0:
            # Criar mesas
            mesas_data = [
                {"numero": 1, "capacidade": 2},
                {"numero": 2, "capacidade": 2},
                {"numero": 3, "capacidade": 4},
                {"numero": 4, "capacidade": 4},
                {"numero": 5, "capacidade": 6},
            ]
            
            for mesa_data in mesas_data:
                mesa = Mesa(numero=mesa_data["numero"], capacidade=mesa_data["capacidade"], status="livre")
                db.session.add(mesa)
            
            db.session.commit()
            print("✓ Mesas criadas com sucesso!")
        
        # Verificar se já tem produtos
        if Produto.query.count() == 0:
            # Criar produtos
            produtos_data = [
                {"nome": "Hambúrguer", "descricao": "Hambúrguer caseiro", "preco": 25.00},
                {"nome": "Pizza Margherita", "descricao": "Pizza tradicional", "preco": 35.00},
                {"nome": "Refrigerante", "descricao": "2L", "preco": 10.00},
                {"nome": "Cerveja", "descricao": "Pilsen 600ml", "preco": 8.00},
                {"nome": "Batata Frita", "descricao": "Porção grande", "preco": 18.00},
                {"nome": "Agua", "descricao": "500ml", "preco": 2.00},
            ]
            
            for produto_data in produtos_data:
                produto = Produto(
                    nome=produto_data["nome"],
                    descricao=produto_data["descricao"],
                    preco=produto_data["preco"],
                    disponivel=True
                )
                db.session.add(produto)
            
            db.session.commit()
            print("✓ Produtos criados com sucesso!")
    
    except Exception as e:
        print(f"⚠ Erro ao popular dados iniciais: {e}")
        db.session.rollback()

app = create_app()

with app.app_context():
    db.create_all()
    seed_initial_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)