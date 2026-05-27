-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: instituteerp
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `certificates`
--

DROP TABLE IF EXISTS `certificates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `course_id` int DEFAULT NULL,
  `issued_at` datetime DEFAULT NULL,
  `certificate_no` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificates`
--

LOCK TABLES `certificates` WRITE;
/*!40000 ALTER TABLE `certificates` DISABLE KEYS */;
INSERT INTO `certificates` VALUES (1,1,1,'2026-02-10 13:17:10','CERT-0E0F1F0F'),(2,1,6,'2026-02-10 13:23:08','CERT-2FE3979A');
/*!40000 ALTER TABLE `certificates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact_details`
--

DROP TABLE IF EXISTS `contact_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contact_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `message` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact_details`
--

LOCK TABLES `contact_details` WRITE;
/*!40000 ALTER TABLE `contact_details` DISABLE KEYS */;
INSERT INTO `contact_details` VALUES (1,'Arpita Patil','arpitapatil@gmail.com','9518559942','hii'),(2,'Diksha Pardesi','dikshapardeshi086@gmail.com','7620158622','My contact details'),(3,'Pooja Pande','poojapande@gmail.com','9518559942','Hii'),(4,'Pooja Pande','poojapande@gmail.com','9518559942','Hii'),(5,'Arpita Patil','arpitapatil@gmail.com','09518559942','Hii'),(6,'Arpita Patil','arpitapatil@gmail.com','09518559942','Hii');
/*!40000 ALTER TABLE `contact_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_reviews`
--

DROP TABLE IF EXISTS `course_reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `user_id` int NOT NULL,
  `rating` int DEFAULT NULL,
  `review` text NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `course_id` (`course_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `course_reviews_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `course_reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `registration` (`id`) ON DELETE CASCADE,
  CONSTRAINT `course_reviews_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_reviews`
--

LOCK TABLES `course_reviews` WRITE;
/*!40000 ALTER TABLE `course_reviews` DISABLE KEYS */;
INSERT INTO `course_reviews` VALUES (1,1,1,5,'Best Course','2026-02-09 20:50:28'),(2,2,1,5,'super','2026-02-10 11:35:01');
/*!40000 ALTER TABLE `course_reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_videos`
--

DROP TABLE IF EXISTS `course_videos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_videos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `video_number` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `video_filename` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `youtube_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_videos`
--

LOCK TABLES `course_videos` WRITE;
/*!40000 ALTER TABLE `course_videos` DISABLE KEYS */;
INSERT INTO `course_videos` VALUES (1,1,1,'Python','Python is a high-level, interpreted, open-source programming language known for its simplicity, readability, and versatility.',NULL,'2026-01-29 15:19:18','https://www.youtube.com/embed/OZIRAavoGng'),(2,2,1,'Django','Django is a high-level, open-source Python web framework used to build secure, scalable, and maintainable web applications quickly.',NULL,'2026-01-29 16:24:54','https://www.youtube.com/embed/5BDgKJFZMl8'),(3,3,1,'React','React is an open-source JavaScript library used for building fast, interactive, and reusable user interfaces, especially for single-page applications (SPAs). It is developed and maintained by Meta (Facebook).','react_video.mp4','2026-01-29 16:26:09',''),(4,3,2,'React','React is an open-source JavaScript library used for building fast, interactive, and reusable user interfaces, especially for single-page applications (SPAs). It is developed and maintained by Meta (Facebook).',NULL,'2026-01-29 16:26:54','https://www.youtube.com/embed/M1ke8lPOAvM'),(6,6,1,'Flask','Flask is a lightweight, \"micro\" web framework for Python, designed for easy setup and flexibility without requiring specific tools or libraries. ',NULL,'2026-02-09 16:26:16','https://www.youtube.com/embed/0HXg9_r_7MM');
/*!40000 ALTER TABLE `course_videos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `description` text,
  `price` int DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `instructor_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,'Python','Python is one of the most popular and powerful programming languages used today in web development, data science, automation, artificial intelligence, and more. This course is designed to take you from beginner to confident Python developer, even if you have no prior coding experience.',999,'python-img1.jpg','2026-01-14 07:18:39',''),(2,'Django','Learn to build secure, scalable web applications using Django.\r\nMaster models, views, templates, and create real-world projects with Python Django.',799,'Django.jpg','2026-01-14 07:20:56',''),(3,'React','Learn to build fast, interactive user interfaces using React.\r\nMaster components, hooks, and state management to create modern web applications.',599,'react-logo-01.png','2026-01-14 07:21:43',''),(4,'Web Development','Learn to build modern, responsive websites using HTML, CSS, JavaScript, and frameworks.\r\nDevelop real-world projects and gain the skills needed to become a full-stack web developer.',699,'web_dev.webp','2026-01-14 07:23:07',''),(5,'PHP','PHP is a powerful server-side scripting language used to build dynamic and interactive websites. It integrates easily with databases like MySQL to create robust web applications.',599,'php.jpg','2026-01-15 06:18:32',''),(6,'Flask',' Flask is a lightweight, \"micro\" web framework for Python, designed for easy setup and flexibility without requiring specific tools or libraries. ',999,'535a8c2ee8bb.jpg','2026-02-09 16:00:00',' Diksha pardeshi');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollments`
--

DROP TABLE IF EXISTS `enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `course_id` int NOT NULL,
  `enrolled_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollments`
--

LOCK TABLES `enrollments` WRITE;
/*!40000 ALTER TABLE `enrollments` DISABLE KEYS */;
INSERT INTO `enrollments` VALUES (1,1,1,'2026-01-15 07:49:34'),(2,1,3,'2026-01-19 07:00:53'),(3,2,1,'2026-01-20 06:01:45'),(4,2,3,'2026-01-20 06:04:30'),(5,2,5,'2026-01-20 06:04:49'),(6,5,1,'2026-01-20 06:10:54'),(7,1,5,'2026-01-20 06:26:45'),(8,1,4,'2026-01-20 06:30:21'),(9,1,6,'2026-02-09 16:27:44');
/*!40000 ALTER TABLE `enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `instructors`
--

DROP TABLE IF EXISTS `instructors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `instructors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instructors`
--

LOCK TABLES `instructors` WRITE;
/*!40000 ALTER TABLE `instructors` DISABLE KEYS */;
INSERT INTO `instructors` VALUES (1,' Diksha pardeshi','dikshapardeshi@gmail.com','diksha16'),(2,'Arpita Patil','arpitapatil@gmail.com','arpita18'),(3,'Pooja Pande','poojapande@gmail.com','pooja28'),(4,' Diksha pardeshi','dikshapardeshi086@gmail.com','diksha16');
/*!40000 ALTER TABLE `instructors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quiz_attempts`
--

DROP TABLE IF EXISTS `quiz_attempts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quiz_attempts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `quiz_id` int DEFAULT NULL,
  `score` int DEFAULT NULL,
  `passed` tinyint(1) DEFAULT NULL,
  `attempted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quiz_attempts`
--

LOCK TABLES `quiz_attempts` WRITE;
/*!40000 ALTER TABLE `quiz_attempts` DISABLE KEYS */;
INSERT INTO `quiz_attempts` VALUES (1,1,1,100,1,'2026-02-09 15:09:11'),(2,1,1,20,0,'2026-02-09 15:10:10'),(3,1,1,100,1,'2026-02-09 15:10:32'),(4,1,1,100,1,'2026-02-09 15:13:04'),(5,1,1,100,1,'2026-02-09 15:15:02'),(6,1,1,100,1,'2026-02-09 15:45:37'),(7,1,2,100,1,'2026-02-09 16:28:05'),(8,1,2,100,1,'2026-02-09 16:28:34'),(9,1,1,100,1,'2026-02-10 06:04:30'),(10,1,1,75,1,'2026-02-24 07:06:45'),(11,1,2,100,1,'2026-02-24 07:07:01');
/*!40000 ALTER TABLE `quiz_attempts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quiz_questions`
--

DROP TABLE IF EXISTS `quiz_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quiz_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quiz_id` int DEFAULT NULL,
  `question` text,
  `option_a` varchar(255) DEFAULT NULL,
  `option_b` varchar(255) DEFAULT NULL,
  `option_c` varchar(255) DEFAULT NULL,
  `option_d` varchar(255) DEFAULT NULL,
  `correct_option` char(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quiz_questions`
--

LOCK TABLES `quiz_questions` WRITE;
/*!40000 ALTER TABLE `quiz_questions` DISABLE KEYS */;
INSERT INTO `quiz_questions` VALUES (6,2,'Flask framework is written in which of the following language?','Java ','Python ','JavaScript','HTML','b'),(12,1,'What is extension of python?','.py','.html','.java','.exe','a'),(13,1,'what is function of python','def()','fun()','function()','define()','a'),(14,1,'Which loop is used to iterate over a sequence?',' while  ','loop ','for ','repeat','c'),(15,1,'Which data type is used to store key–value pairs in Python?',' List ','Tuple ','Dictionary','Set','c');
/*!40000 ALTER TABLE `quiz_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quizzes`
--

DROP TABLE IF EXISTS `quizzes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quizzes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `pass_percentage` int DEFAULT '50',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quizzes`
--

LOCK TABLES `quizzes` WRITE;
/*!40000 ALTER TABLE `quizzes` DISABLE KEYS */;
INSERT INTO `quizzes` VALUES (1,1,'Python',50,'2026-02-09 15:08:20'),(2,6,'Flask',50,'2026-02-09 16:02:31');
/*!40000 ALTER TABLE `quizzes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration`
--

DROP TABLE IF EXISTS `registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration`
--

LOCK TABLES `registration` WRITE;
/*!40000 ALTER TABLE `registration` DISABLE KEYS */;
INSERT INTO `registration` VALUES (1,' Diksha pardeshi','dikshapardeshi086@gmail.com','diksha','diksha16'),(2,'Arpita Patil','arpitapatil@gmail.com','arpita','arpita18'),(3,'amar','amar@gmail.com','amar tiwari','main'),(4,'Pooja Pande','poojapande@gmail.com','pooja pande','pooja12'),(5,'Anaya Pande','anayapande@gmail.com','anaya ','anaya14'),(6,'Samrudhi Gupta','samrudhigupta@gmail.com','samrudhi','samrudhi20'),(7,'jay','jay@gmail.com','jay','main123');
/*!40000 ALTER TABLE `registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resume_data`
--

DROP TABLE IF EXISTS `resume_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resume_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(150) NOT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `address` text,
  `photo` varchar(255) DEFAULT NULL,
  `summary` text,
  `skills` text,
  `education_10` varchar(255) DEFAULT NULL,
  `education_12` varchar(255) DEFAULT NULL,
  `education_degree` varchar(255) DEFAULT NULL,
  `education_pg` varchar(255) DEFAULT NULL,
  `certificates` text,
  `projects` text,
  `experiences` text,
  `linkedin` varchar(255) DEFAULT NULL,
  `github` varchar(255) DEFAULT NULL,
  `template_id` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `resume_data_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `registration` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resume_data`
--

LOCK TABLES `resume_data` WRITE;
/*!40000 ALTER TABLE `resume_data` DISABLE KEYS */;
INSERT INTO `resume_data` VALUES (1,1,'Diksha Jitendra Pardesi','7620158622','dikshapardeshi086@gmail.com','Rukhmini Nagar, Amravati','images_1.jpg','Detail-oriented and motivated IT graduate with a strong foundation in software development, databases, and web technologies. Skilled in Python, HTML, CSS, and SQL, with hands-on experience in academic and project-based environments. Quick learner with strong problem-solving abilities, eager to contribute to innovative IT solutions and grow within a professional organization.','Python, HTML, CSS, Java, Flask','Takhatmal English High School, Amravati 2020',' Matoshree Vimalabai Deshmukh Mahavidyalaya, Amravati 2022','BCA Degree College of Physical Education, HVPM, Amravati 2025','MCA Vidya Bharati Mahavidyalaya (VBMV) 2026','Python Full Stack Development (Laksh IT Solution), Java Full Stack Development (Laksh IT Solution)','Institute ERP - Developed an Institute ERP system with Admin Instructor and User modules to manage academic activities user information and course processes through a centralized and user-friendly application, HR-ERP System - Developed an HR-ERP system with Admin and Employee modules to manage employee records attendance leave and payroll through a secure and user-friendly application','Python Internship - Experience in Python coding testing and debugging through live projects, Software Development - Involved in designing developing and testing software applications using programming languages and tools to deliver efficient and user-friendly solutions','https://linkedin.com/dikshapardesi','https://github.com/dikshapardesi',1,'2026-01-28 07:19:09','2026-02-04 06:57:20'),(2,1,'Arpita Patil','9518559942','arpitapatil@gmail.com',' Rajput pura','images.jpg','This is dddd','fdd','Takhatmal English High School 2020',' Matoshree Vimalabai Deshmukh Mahavidyalaya, HVPM 2022','ddddd','dd','Python Full Stack Development (Laksh IT Solution)','','','https://linkedin.com/dikshapardesi','https://github.com/dikshapardesi',1,'2026-02-04 06:57:15','2026-02-04 06:57:15');
/*!40000 ALTER TABLE `resume_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_course_progress`
--

DROP TABLE IF EXISTS `user_course_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_course_progress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `course_id` int NOT NULL,
  `completed_videos` int DEFAULT '0',
  `total_videos` int DEFAULT '0',
  `progress_percent` int DEFAULT '0',
  `completed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_course_unique` (`user_id`,`course_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `user_course_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `registration` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_course_progress_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_course_progress`
--

LOCK TABLES `user_course_progress` WRITE;
/*!40000 ALTER TABLE `user_course_progress` DISABLE KEYS */;
INSERT INTO `user_course_progress` VALUES (1,1,1,1,1,100,1),(2,1,3,2,2,100,1),(6,1,6,1,1,100,1);
/*!40000 ALTER TABLE `user_course_progress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `video_progress`
--

DROP TABLE IF EXISTS `video_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `video_progress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `course_id` int NOT NULL,
  `video_id` int NOT NULL,
  `completed` tinyint(1) DEFAULT '0',
  `completed_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_video_unique` (`user_id`,`video_id`),
  KEY `course_id` (`course_id`),
  KEY `video_id` (`video_id`),
  CONSTRAINT `video_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `registration` (`id`) ON DELETE CASCADE,
  CONSTRAINT `video_progress_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `video_progress_ibfk_3` FOREIGN KEY (`video_id`) REFERENCES `course_videos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `video_progress`
--

LOCK TABLES `video_progress` WRITE;
/*!40000 ALTER TABLE `video_progress` DISABLE KEYS */;
INSERT INTO `video_progress` VALUES (1,1,1,1,1,'2026-02-10 13:17:09'),(2,1,3,3,1,'2026-02-24 12:37:13'),(3,1,3,4,1,'2026-02-10 13:16:29'),(6,1,6,6,1,'2026-02-10 13:23:08');
/*!40000 ALTER TABLE `video_progress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist`
--

DROP TABLE IF EXISTS `wishlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `course_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_wishlist` (`user_id`,`course_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `registration` (`id`) ON DELETE CASCADE,
  CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist`
--

LOCK TABLES `wishlist` WRITE;
/*!40000 ALTER TABLE `wishlist` DISABLE KEYS */;
INSERT INTO `wishlist` VALUES (1,1,1,'2026-02-09 15:19:14');
/*!40000 ALTER TABLE `wishlist` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-17 20:35:51
