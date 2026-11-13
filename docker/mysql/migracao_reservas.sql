-- Reservas de mesas e lista de espera.
-- O app também cria essas tabelas automaticamente (db.create_all) ao iniciar.

CREATE TABLE IF NOT EXISTS `reservas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_nome` varchar(100) NOT NULL,
  `contato` varchar(120) NOT NULL,
  `data` date NOT NULL,
  `horario` time NOT NULL,
  `quantidade_pessoas` int(11) NOT NULL,
  `mesa_id` int(11) NOT NULL,
  `observacao` varchar(255) DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'confirmada',
  `pedido_id` int(11) DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_reservas_data` (`data`),
  KEY `ix_reservas_mesa_id` (`mesa_id`),
  KEY `ix_reservas_status` (`status`),
  CONSTRAINT `fk_reservas_mesa` FOREIGN KEY (`mesa_id`) REFERENCES `mesas` (`id`),
  CONSTRAINT `fk_reservas_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `lista_espera` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `contato` varchar(120) NOT NULL,
  `quantidade_pessoas` int(11) NOT NULL,
  `entrada_em` datetime NOT NULL,
  `observacao` varchar(255) DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'aguardando',
  `reserva_id` int(11) DEFAULT NULL,
  `mesa_id` int(11) DEFAULT NULL,
  `pedido_id` int(11) DEFAULT NULL,
  `atendido_em` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_lista_espera_entrada_em` (`entrada_em`),
  KEY `ix_lista_espera_status` (`status`),
  CONSTRAINT `fk_lista_espera_reserva` FOREIGN KEY (`reserva_id`) REFERENCES `reservas` (`id`),
  CONSTRAINT `fk_lista_espera_mesa` FOREIGN KEY (`mesa_id`) REFERENCES `mesas` (`id`),
  CONSTRAINT `fk_lista_espera_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
