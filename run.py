from app import create_app
from app.extensions import db
from app.models import mesa, pedido, produto, item_pedido, categoria
from app.models import pagamento
from app.models.mesa import Mesa
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.categorias import CATEGORIAS_PRODUTO

def seed_initial_data():
    """Popula o banco com dados iniciais se estiver vazio"""
    try:
        # Criar categorias iniciais (se ainda não houver nenhuma)
        if Categoria.query.count() == 0:
            for nome in CATEGORIAS_PRODUTO:
                db.session.add(Categoria(nome=nome))
            db.session.commit()
            print("✓ Categorias criadas com sucesso!")

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
            # Mapa nome-da-categoria -> id (para associar cada produto)
            cat_map = {c.nome: c.id for c in Categoria.query.all()}

            # Criar produtos (já associados a uma categoria)
            produtos_data = [
                {"nome": "Hambúrguer", "descricao": "Hambúrguer caseiro", "preco": 25.00, "categoria": "Pratos Principais"},
                {"nome": "Pizza Margherita", "descricao": "Pizza tradicional", "preco": 35.00, "categoria": "Pratos Principais"},
                {"nome": "Refrigerante", "descricao": "2L", "preco": 10.00, "categoria": "Bebidas"},
                {"nome": "Cerveja", "descricao": "Pilsen 600ml", "preco": 8.00, "categoria": "Bebidas"},
                {"nome": "Batata Frita", "descricao": "Porção grande", "preco": 18.00, "categoria": "Porções"},
                {"nome": "Agua", "descricao": "500ml", "preco": 2.00, "categoria": "Bebidas"},
                {"nome": "X-Burger", "descricao": "Pão com carne, acompanhado com queijo americano, tomates e alface", "preco": 10.00, "categoria": "Pratos Principais"},
                {"nome": "Anéis de Cebola", "descricao": "Anéis de cebola fritos, acompanhando 10 unidades", "preco": 13.00, "categoria": "Porções"},
                {"nome": "Salmão", "descricao": "Salmão Grelhado", "preco": 60.00, "categoria": "Pratos Principais"},
            ]

            for produto_data in produtos_data:
                produto = Produto(
                    nome=produto_data["nome"],
                    descricao=produto_data["descricao"],
                    preco=produto_data["preco"],
                    disponivel=True,
                    categoria_id=cat_map.get(produto_data.get("categoria"))
                )
                db.session.add(produto)

            db.session.commit()
            print("✓ Produtos criados com sucesso!")
    
    except Exception as e:
        print(f"⚠ Erro ao popular dados iniciais: {e}")
        db.session.rollback()

app = create_app()

with app.app_context():
    try:
        db.create_all()
        seed_initial_data()
    except Exception as e:
        print(f"⚠  Não foi possível inicializar o banco: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)