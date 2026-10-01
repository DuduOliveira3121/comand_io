-- Migração para bancos existentes: acrescenta o identificador PIX e permite
-- identificar pagamentos cancelados pela aplicação.
-- Rode UMA vez: mysql -uroot -p restaurante < docker/mysql/migracao_pagamento_txid.sql

ALTER TABLE `pagamentos`
  ADD COLUMN `txid` varchar(36) DEFAULT NULL,
  ADD UNIQUE KEY `uq_pagamentos_txid` (`txid`);