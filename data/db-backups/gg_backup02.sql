-- MySQL dump 10.13  Distrib 5.6.26, for osx10.8 (x86_64)
--
-- Host: localhost    Database: grade_grabber
-- ------------------------------------------------------
-- Server version	5.6.26

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courses` (
  `c_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(4) NOT NULL,
  `course_number` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  PRIMARY KEY (`c_id`)
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (155,'AAS',100,'Intro Asian American Studies'),(156,'AAS',211,'Asian Americans and the Arts'),(157,'AAS',258,'Muslims in America'),(158,'AAS',287,'Food and Asian Americans'),(159,'AAS',390,'Race, Memory, and Violence'),(160,'AAS',490,'Social Movements'),(161,'ABE',100,'Intro Agric & Biological Engrg'),(162,'ABE',199,'Undergraduate Open Seminar'),(163,'ABE',223,'ABE Principles: Machine Syst'),(164,'ABE',224,'ABE Principles: Soil & Water'),(165,'ABE',341,'Transport Processes in ABE'),(166,'ABE',361,'Off-Road Machine Design'),(167,'ABE',398,'International Experience'),(168,'ABE',430,'Project Management'),(169,'ABE',455,'Erosion and Sediment Control'),(170,'ABE',463,'Electrohydraulic Systems'),(171,'ABE',466,'Engineering Off-Road Vehicles'),(172,'ABE',483,'Engrg Properties of Food Matls'),(173,'ABE',488,'Bioprocessing Biomass for Fuel'),(174,'ACCY',200,'Fundamentals of Accounting'),(175,'ACCY',201,'Accounting and Accountancy I'),(176,'ACCY',202,'Accounting and Accountancy II'),(177,'ACCY',301,'Atg Measurement & Disclosure'),(178,'ACCY',302,'Decision Making for Atg'),(179,'ACCY',303,'Atg Institutions and Reg'),(180,'ACCY',304,'Accounting Control Systems'),(181,'ACCY',312,'Principles of Taxation'),(182,'ACCY',398,'Practical Problems in Atg'),(183,'ACCY',405,'Assurance and Attestation'),(184,'ACCY',410,'Advanced Financial Reporting'),(194,'1',2,'3'),(202,'3',4,'5'),(203,'5',7,'9'),(204,'11',12,'13');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grade_counts`
--

DROP TABLE IF EXISTS `grade_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `grade_counts` (
  `c_id` int(11) NOT NULL,
  `s_id` int(11) NOT NULL,
  `average_gpa` decimal(3,2) DEFAULT NULL,
  `a_plus_count` int(11) DEFAULT NULL,
  `a_count` int(11) DEFAULT NULL,
  `a_minus_count` int(11) DEFAULT NULL,
  `b_plus_count` int(11) DEFAULT NULL,
  `b_count` int(11) DEFAULT NULL,
  `b_minus_count` int(11) DEFAULT NULL,
  `c_plus_count` int(11) DEFAULT NULL,
  `c_count` int(11) DEFAULT NULL,
  `c_minus_count` int(11) DEFAULT NULL,
  `d_plus_count` int(11) DEFAULT NULL,
  `d_count` int(11) DEFAULT NULL,
  `d_minus_count` int(11) DEFAULT NULL,
  `f_count` int(11) DEFAULT NULL,
  `w_count` int(11) DEFAULT NULL,
  UNIQUE KEY `c_id` (`c_id`,`s_id`),
  KEY `s_id` (`s_id`),
  CONSTRAINT `grade_counts_ibfk_1` FOREIGN KEY (`c_id`) REFERENCES `courses` (`c_id`) ON UPDATE CASCADE,
  CONSTRAINT `grade_counts_ibfk_2` FOREIGN KEY (`s_id`) REFERENCES `semesters` (`s_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grade_counts`
--

LOCK TABLES `grade_counts` WRITE;
/*!40000 ALTER TABLE `grade_counts` DISABLE KEYS */;
/*!40000 ALTER TABLE `grade_counts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semesters`
--

DROP TABLE IF EXISTS `semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `semesters` (
  `c_id` int(11) NOT NULL,
  `s_id` int(11) NOT NULL AUTO_INCREMENT,
  `crn` varchar(6) NOT NULL,
  `raw_term` varchar(6) NOT NULL,
  `parsed_term` varchar(4) NOT NULL,
  `section` varchar(4) NOT NULL,
  `instructor` varchar(75) NOT NULL,
  PRIMARY KEY (`s_id`),
  KEY `c_id` (`c_id`),
  CONSTRAINT `semesters_ibfk_1` FOREIGN KEY (`c_id`) REFERENCES `courses` (`c_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semesters`
--

LOCK TABLES `semesters` WRITE;
/*!40000 ALTER TABLE `semesters` DISABLE KEYS */;
/*!40000 ALTER TABLE `semesters` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-04-14 13:38:26
