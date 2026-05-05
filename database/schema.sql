-- MySQL dump 10.13  Distrib 9.0.1, for macos14 (x86_64)
--
-- Host: localhost    Database: gestproy
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `criterios_aceptacion`
--

DROP TABLE IF EXISTS `criterios_aceptacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `criterios_aceptacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requerimiento_id` int NOT NULL,
  `descripcion` text NOT NULL,
  `cumplido` tinyint(1) NOT NULL DEFAULT '0',
  `orden` int NOT NULL DEFAULT '0',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `requerimiento_id` (`requerimiento_id`),
  CONSTRAINT `criterios_aceptacion_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimientos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `diagramas`
--

DROP TABLE IF EXISTS `diagramas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagramas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proyecto_id` int NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `datos` json NOT NULL,
  `creado_por` int NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `proyecto_id` (`proyecto_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `diagramas_ibfk_1` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `diagramas_ibfk_2` FOREIGN KEY (`creado_por`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ejecuciones_tecnica`
--

DROP TABLE IF EXISTS `ejecuciones_tecnica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ejecuciones_tecnica` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subproceso_tecnica_id` int NOT NULL,
  `datos` json NOT NULL,
  `participantes` text,
  `fecha_ejecucion` date DEFAULT NULL,
  `estado` enum('planificada','en_progreso','completada') NOT NULL DEFAULT 'planificada',
  `notas` text,
  `creado_por` int NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `subproceso_tecnica_id` (`subproceso_tecnica_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `ejecuciones_tecnica_ibfk_1` FOREIGN KEY (`subproceso_tecnica_id`) REFERENCES `subproceso_tecnicas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ejecuciones_tecnica_ibfk_2` FOREIGN KEY (`creado_por`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `miembros_proyecto`
--

DROP TABLE IF EXISTS `miembros_proyecto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `miembros_proyecto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proyecto_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `rol_id` int NOT NULL,
  `asignado_por` int DEFAULT NULL,
  `fecha_asignacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_proyecto_usuario` (`proyecto_id`,`usuario_id`),
  KEY `fk_mp_usuario` (`usuario_id`),
  KEY `fk_mp_rol` (`rol_id`),
  KEY `fk_mp_asignador` (`asignado_por`),
  CONSTRAINT `fk_mp_asignador` FOREIGN KEY (`asignado_por`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `fk_mp_proyecto` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_mp_rol` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `fk_mp_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `procesos`
--

DROP TABLE IF EXISTS `procesos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `procesos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proyecto_id` int NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `objetivo` text,
  `responsable_id` int DEFAULT NULL,
  `estado` enum('definido','en_progreso','completado') NOT NULL DEFAULT 'definido',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_proc_proyecto` (`proyecto_id`),
  KEY `fk_proc_responsable` (`responsable_id`),
  CONSTRAINT `fk_proc_proyecto` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_proc_responsable` FOREIGN KEY (`responsable_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proyectos`
--

DROP TABLE IF EXISTS `proyectos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyectos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `estado` enum('iniciado','en_progreso','completado') NOT NULL DEFAULT 'iniciado',
  `prioridad` enum('baja','media','alta') NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `creado_por` int NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_proyectos_creador` (`creado_por`),
  CONSTRAINT `fk_proyectos_creador` FOREIGN KEY (`creado_por`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `requerimientos`
--

DROP TABLE IF EXISTS `requerimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `requerimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subproceso_id` int NOT NULL,
  `subproceso_tecnica_id` int NOT NULL,
  `codigo` varchar(30) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text,
  `tipo` enum('funcional','no_funcional','restriccion','regla_negocio') NOT NULL DEFAULT 'funcional',
  `prioridad` enum('critica','alta','media','baja') NOT NULL DEFAULT 'media',
  `estado` enum('borrador','propuesto','aprobado','rechazado') NOT NULL DEFAULT 'borrador',
  `metadata` json DEFAULT NULL,
  `creado_por` int NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_codigo_subproceso` (`subproceso_id`,`codigo`),
  KEY `subproceso_tecnica_id` (`subproceso_tecnica_id`),
  KEY `creado_por` (`creado_por`),
  CONSTRAINT `requerimientos_ibfk_1` FOREIGN KEY (`subproceso_id`) REFERENCES `subprocesos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `requerimientos_ibfk_2` FOREIGN KEY (`subproceso_tecnica_id`) REFERENCES `subproceso_tecnicas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `requerimientos_ibfk_3` FOREIGN KEY (`creado_por`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proyecto_id` int DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `es_fijo` tinyint(1) NOT NULL DEFAULT '0',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_roles_proyecto` (`proyecto_id`),
  CONSTRAINT `fk_roles_proyecto` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stakeholders`
--

DROP TABLE IF EXISTS `stakeholders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stakeholders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proyecto_id` int NOT NULL,
  `nombre_completo` varchar(200) NOT NULL,
  `correo` varchar(255) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `organizacion` varchar(200) DEFAULT NULL,
  `cargo` varchar(150) DEFAULT NULL,
  `tipo` enum('interno','externo','patrocinador','cliente','proveedor') NOT NULL,
  `nivel_influencia_interes` enum('bajo','medio','alto') NOT NULL,
  `notas` text,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_sh_proyecto` (`proyecto_id`),
  CONSTRAINT `fk_sh_proyecto` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subproceso_tecnicas`
--

DROP TABLE IF EXISTS `subproceso_tecnicas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subproceso_tecnicas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subproceso_id` int NOT NULL,
  `tecnica_id` int NOT NULL,
  `notas` text,
  `fecha_asignacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_sub_tecnica` (`subproceso_id`,`tecnica_id`),
  KEY `fk_st_tecnica` (`tecnica_id`),
  CONSTRAINT `fk_st_subproceso` FOREIGN KEY (`subproceso_id`) REFERENCES `subprocesos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_st_tecnica` FOREIGN KEY (`tecnica_id`) REFERENCES `tecnicas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subprocesos`
--

DROP TABLE IF EXISTS `subprocesos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subprocesos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proceso_id` int NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `responsable_id` int DEFAULT NULL,
  `estado` enum('definido','en_progreso','completado') NOT NULL DEFAULT 'definido',
  `horas_estimadas` decimal(8,2) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_sub_proceso` (`proceso_id`),
  KEY `fk_sub_responsable` (`responsable_id`),
  CONSTRAINT `fk_sub_proceso` FOREIGN KEY (`proceso_id`) REFERENCES `procesos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sub_responsable` FOREIGN KEY (`responsable_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tecnicas`
--

DROP TABLE IF EXISTS `tecnicas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tecnicas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `categoria` varchar(50) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-01  2:27:23
-- MySQL dump 10.13  Distrib 9.0.1, for macos14 (x86_64)
--
-- Host: localhost    Database: gestproy
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `tecnicas`
--

LOCK TABLES `tecnicas` WRITE;
/*!40000 ALTER TABLE `tecnicas` DISABLE KEYS */;
INSERT INTO `tecnicas` VALUES (2,'Entrevista individual','Entrevista uno a uno con stakeholder','entrevista',1,'2026-05-01 02:04:04'),(3,'Entrevista grupal','Entrevista con multiples stakeholders','entrevista',1,'2026-05-01 02:04:04'),(4,'Cuestionario abierto','Cuestionario con preguntas abiertas','cuestionario',1,'2026-05-01 02:04:04'),(5,'Cuestionario mixto','Cuestionario con preguntas abiertas y cerradas','cuestionario',1,'2026-05-01 02:04:04'),(6,'Observacion directa','Observacion del proceso en su contexto','observacion',1,'2026-05-01 02:04:04'),(7,'Observacion participante','Observacion participando en el proceso','observacion',1,'2026-05-01 02:04:04'),(8,'Brainstorming clasico','Sesion de lluvia de ideas libre','brainstorming',1,'2026-05-01 02:04:04'),(9,'Brainstorming inverso','Identificar problemas para encontrar soluciones','brainstorming',1,'2026-05-01 02:04:04'),(10,'Analisis de documentos','Revision de documentacion existente','analisis_documental',1,'2026-05-01 02:04:04'),(11,'Analisis de sistemas actuales','Estudio de sistemas en operacion','analisis_documental',1,'2026-05-01 02:04:04'),(12,'Casos de uso','Definicion de escenarios de uso del sistema','casos_de_uso',1,'2026-05-01 02:04:04'),(13,'Historias de usuario','Funcionalidad desde perspectiva del usuario','casos_de_uso',1,'2026-05-01 02:04:04'),(14,'Prototipo de baja fidelidad','Bocetos y wireframes basicos','prototipado',1,'2026-05-01 02:04:04'),(15,'Prototipo de alta fidelidad','Prototipo interactivo detallado','prototipado',1,'2026-05-01 02:04:04');
/*!40000 ALTER TABLE `tecnicas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-01  2:27:23
