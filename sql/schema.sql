CREATE DATABASE IF NOT EXISTS enterprise_assistant
    DEFAULT CHARACTER SET utf8mb4;

USE enterprise_assistant;

CREATE TABLE IF NOT EXISTS `enterprise_assistant` (
  `application_id` varchar(64) NOT NULL,
  `applicant_id` varchar(64) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(64) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`application_id`),
  CONSTRAINT `enterprise_assistant_chk_1` CHECK ((`amount` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;