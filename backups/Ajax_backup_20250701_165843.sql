-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: Ajax
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `alarm_history`
--

DROP TABLE IF EXISTS `alarm_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alarm_history` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Alarm_Type` varchar(255) NOT NULL,
  `Message` text,
  `Event_datetime` datetime DEFAULT CURRENT_TIMESTAMP,
  `User` varchar(50) DEFAULT NULL,
  `Acknowledge_datetime` datetime DEFAULT NULL,
  `Accept_datetime` datetime DEFAULT NULL,
  `Normalise_datetime` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm_history`
--

LOCK TABLES `alarm_history` WRITE;
/*!40000 ALTER TABLE `alarm_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `alarm_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `batches`
--

DROP TABLE IF EXISTS `batches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batches` (
  `Batch_ID` int NOT NULL AUTO_INCREMENT,
  `SalesOrderID` int DEFAULT NULL,
  `Batch_Series_ID` int DEFAULT NULL,
  `Batch_Number` int DEFAULT NULL,
  `DateTime` datetime DEFAULT NULL,
  `20MM` float DEFAULT NULL,
  `10MM` float DEFAULT NULL,
  `R_Sand` float DEFAULT NULL,
  `C_Sand` float DEFAULT NULL,
  `MT` float DEFAULT NULL,
  `CMT1` float DEFAULT NULL,
  `CMT2` float DEFAULT NULL,
  `WTR1` float DEFAULT NULL,
  `ADM1` float DEFAULT NULL,
  `ADM2` float DEFAULT NULL,
  `Quantity` float DEFAULT NULL,
  PRIMARY KEY (`Batch_ID`),
  KEY `SalesOrderID` (`SalesOrderID`),
  CONSTRAINT `batches_ibfk_1` FOREIGN KEY (`SalesOrderID`) REFERENCES `sales_order` (`SalesOrderID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batches`
--

LOCK TABLES `batches` WRITE;
/*!40000 ALTER TABLE `batches` DISABLE KEYS */;
/*!40000 ALTER TABLE `batches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `client_details`
--

DROP TABLE IF EXISTS `client_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `client_details` (
  `Client_ID` int NOT NULL AUTO_INCREMENT,
  `Client_Name` varchar(100) DEFAULT NULL,
  `Site` varchar(100) DEFAULT NULL,
  `Address` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Client_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `client_details`
--

LOCK TABLES `client_details` WRITE;
/*!40000 ALTER TABLE `client_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `client_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mix_design`
--

DROP TABLE IF EXISTS `mix_design`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mix_design` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `MixdesignName` varchar(255) DEFAULT NULL,
  `Grade` varchar(255) DEFAULT NULL,
  `MixingTime` float DEFAULT NULL,
  `20MM` float DEFAULT NULL,
  `10MM` float DEFAULT NULL,
  `R_Sand` float DEFAULT NULL,
  `C_Sand` float DEFAULT NULL,
  `MT` float DEFAULT NULL,
  `CMT1` float DEFAULT NULL,
  `CMT2` float DEFAULT NULL,
  `WTR1` float DEFAULT NULL,
  `ADM1` float DEFAULT NULL,
  `ADM2` float DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mix_design`
--

LOCK TABLES `mix_design` WRITE;
/*!40000 ALTER TABLE `mix_design` DISABLE KEYS */;
/*!40000 ALTER TABLE `mix_design` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `operator_parameters`
--

DROP TABLE IF EXISTS `operator_parameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `operator_parameters` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Defination` varchar(255) DEFAULT NULL,
  `Moisture` float DEFAULT NULL,
  `Tolerance` float DEFAULT NULL,
  `Flight_Weight` float DEFAULT NULL,
  `Recalculate` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operator_parameters`
--

LOCK TABLES `operator_parameters` WRITE;
/*!40000 ALTER TABLE `operator_parameters` DISABLE KEYS */;
INSERT INTO `operator_parameters` VALUES (1,'MT',0,0,0,0),(2,'CMT1',0,0,0,0),(3,'CMT2',0,0,0,0),(4,'CMT3',0,0,0,0),(5,'WTR1',0,0,0,0),(6,'ADM1',0,0,0,0),(7,'ADM2',0,0,0,0);
/*!40000 ALTER TABLE `operator_parameters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_container_settings`
--

DROP TABLE IF EXISTS `product_container_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_container_settings` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Product_Code` varchar(255) DEFAULT NULL,
  `Defination` varchar(255) DEFAULT NULL,
  `Large_Jog_Weight` float DEFAULT NULL,
  `Large_Jog_Time` float DEFAULT NULL,
  `Small_Jog_Time` float DEFAULT NULL,
  `Weighting_Mode` float DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_container_settings`
--

LOCK TABLES `product_container_settings` WRITE;
/*!40000 ALTER TABLE `product_container_settings` DISABLE KEYS */;
INSERT INTO `product_container_settings` VALUES (1,'CMT1','CMT1',5,1,0.5,1),(2,'CMT2','CMT2',5,1,0.5,1),(3,'CMT3','CMT3',5,1,0.5,1),(4,'WTR1','WTR1',5,1,0.5,1),(5,'ADT1','ADT1',5,1,0.5,1),(6,'ADT2','ADT2',5,1,0.5,1);
/*!40000 ALTER TABLE `product_container_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_settings`
--

DROP TABLE IF EXISTS `product_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_settings` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Scales` varchar(255) DEFAULT NULL,
  `Dead_Weight` float DEFAULT NULL,
  `Fill_time` float DEFAULT NULL,
  `Discharge_time` float DEFAULT NULL,
  `Loading_Sequence` float DEFAULT NULL,
  `Jog_Close_Time` float DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_settings`
--

LOCK TABLES `product_settings` WRITE;
/*!40000 ALTER TABLE `product_settings` DISABLE KEYS */;
INSERT INTO `product_settings` VALUES (1,'Cement',10,5,10,1,2),(2,'Water',0.5,5,10,2,2),(3,'Admixture',10,5,10,4,2);
/*!40000 ALTER TABLE `product_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qc_control`
--

DROP TABLE IF EXISTS `qc_control`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qc_control` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Material_Code` varchar(225) DEFAULT NULL,
  `Material_Name` varchar(225) NOT NULL,
  `Specific_Gravity` float NOT NULL,
  `Action` varchar(45) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qc_control`
--

LOCK TABLES `qc_control` WRITE;
/*!40000 ALTER TABLE `qc_control` DISABLE KEYS */;
INSERT INTO `qc_control` VALUES (1,'MTL001','RSand',2.65,'1');
/*!40000 ALTER TABLE `qc_control` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales_order`
--

DROP TABLE IF EXISTS `sales_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_order` (
  `SalesOrderID` int NOT NULL AUTO_INCREMENT,
  `Mix_Name` varchar(100) DEFAULT NULL,
  `Client_ID` int DEFAULT NULL,
  `DateTime` datetime DEFAULT NULL,
  `Ordered_Qty` float DEFAULT NULL,
  `Load_Qty` float DEFAULT NULL,
  `Produced_Qty` float DEFAULT NULL,
  `MixingTime` float DEFAULT NULL,
  PRIMARY KEY (`SalesOrderID`),
  KEY `Client_ID` (`Client_ID`),
  CONSTRAINT `sales_order_ibfk_1` FOREIGN KEY (`Client_ID`) REFERENCES `client_details` (`Client_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_order`
--

LOCK TABLES `sales_order` WRITE;
/*!40000 ALTER TABLE `sales_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `sales_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transport_log`
--

DROP TABLE IF EXISTS `transport_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transport_log` (
  `Transport_ID` int NOT NULL AUTO_INCREMENT,
  `SalesOrderID` int DEFAULT NULL,
  `Batch_ID` int DEFAULT NULL,
  `Batch_Series_ID` int DEFAULT NULL,
  `Truck_Number` varchar(50) DEFAULT NULL,
  `Driver_Name` varchar(100) DEFAULT NULL,
  `Transport_DateTime` datetime DEFAULT NULL,
  `Delivered_Qty` float DEFAULT NULL,
  PRIMARY KEY (`Transport_ID`),
  KEY `SalesOrderID` (`SalesOrderID`),
  KEY `Batch_ID` (`Batch_ID`),
  CONSTRAINT `transport_log_ibfk_1` FOREIGN KEY (`SalesOrderID`) REFERENCES `sales_order` (`SalesOrderID`),
  CONSTRAINT `transport_log_ibfk_2` FOREIGN KEY (`Batch_ID`) REFERENCES `batches` (`Batch_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transport_log`
--

LOCK TABLES `transport_log` WRITE;
/*!40000 ALTER TABLE `transport_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `transport_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(255) DEFAULT NULL,
  `Password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Admin','Admin'),(2,'Operator','Operator'),(3,'OEM','OEM');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicle_details`
--

DROP TABLE IF EXISTS `vehicle_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicle_details` (
  `Vehicle_ID` int NOT NULL AUTO_INCREMENT,
  `Client_ID` int DEFAULT NULL,
  `Vehicle_Type` varchar(100) DEFAULT NULL,
  `Vehicle_Quantity` varchar(100) DEFAULT NULL,
  `Vehicle_Number` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Vehicle_ID`),
  KEY `Client_ID` (`Client_ID`),
  CONSTRAINT `vehicle_details_ibfk_1` FOREIGN KEY (`Client_ID`) REFERENCES `client_details` (`Client_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicle_details`
--

LOCK TABLES `vehicle_details` WRITE;
/*!40000 ALTER TABLE `vehicle_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `vehicle_details` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-01 16:58:43
