-- Migração: adiciona categorias (tabela + FK) e o tipo de pedido em bancos
-- JÁ EXISTENTES. Rode UMA vez. Para um banco novo, o init/restaurante.sql
-- já traz tudo e esta migração não é necessária.
--
-- Como rodar (exemplos):
--   Docker:  docker exec -i <container_mysql> mysql -uroot -p<senha> restaurante < docker/mysql/migracao_categoria.sql
--   Local:   mysql -uroot -p restaurante < docker/mysql/migracao_categoria.sql

-- 1) Tabela de categorias
CREATE TABLE IF NOT EXISTS `categorias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2) Categorias iniciais
INSERT INTO `categorias` (`nome`) VALUES
  ('Bebidas'), ('Entradas'), ('Pratos Principais'), ('Sobremesas'), ('Porções');

-- 3) Coluna categoria_id em produtos + chave estrangeira
ALTER TABLE `produtos`
  ADD COLUMN `categoria_id` int(11) DEFAULT NULL,
  ADD KEY `categoria_id` (`categoria_id`),
  ADD CONSTRAINT `produtos_ibfk_1` FOREIGN KEY (`categoria_id`)
      REFERENCES `categorias` (`id`) ON DELETE SET NULL;

-- 4) Tipo de pedido (comanda): Mesa, Balcão, Delivery, Viagem
ALTER TABLE `pedidos`
  ADD COLUMN `categoria` varchar(50) DEFAULT 'Mesa';
