-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 16, 2026 at 06:28 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `exam`
--

-- --------------------------------------------------------

--
-- Table structure for table `exams`
--

CREATE TABLE `exams` (
  `exam_id` int(11) NOT NULL,
  `subject_id` int(11) DEFAULT NULL,
  `exam_name` varchar(100) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `total_marks` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `exams`
--

INSERT INTO `exams` (`exam_id`, `subject_id`, `exam_name`, `duration`, `total_marks`) VALUES
(1, 11, 'RDBMS Exam', 30, 20);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `student_name` varchar(100) DEFAULT NULL,
  `subject_name` varchar(100) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `student_id`, `student_name`, `subject_name`, `message`, `is_read`, `created_at`) VALUES
(1, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-26 18:45:52'),
(2, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:16:47'),
(3, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:20:12'),
(4, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:20:24'),
(5, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:20:34'),
(6, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:21:58'),
(7, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:24:20'),
(8, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:29:51'),
(9, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:32:45'),
(10, 7, 'dhaval patel', 'RDBMS', 'New Exam Submitted by dhaval patel (RDBMS)', 1, '2026-07-27 14:33:14'),
(11, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:00:04'),
(12, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:00:27'),
(13, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:05:48'),
(14, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:18:17'),
(15, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:31:19'),
(16, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:42:42'),
(17, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:43:48'),
(18, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:44:58'),
(19, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 11:45:34'),
(20, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 12:23:00'),
(21, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 12:40:51'),
(22, 5, 'manaliii', 'RDBMS', 'New Exam Submitted by manaliii (RDBMS)', 1, '2026-07-29 12:41:41');

-- --------------------------------------------------------

--
-- Table structure for table `questions`
--

CREATE TABLE `questions` (
  `id` int(11) NOT NULL,
  `subject_id` int(11) DEFAULT NULL,
  `question_text` text DEFAULT NULL,
  `option1` varchar(255) DEFAULT NULL,
  `option2` varchar(255) DEFAULT NULL,
  `option3` varchar(255) DEFAULT NULL,
  `option4` varchar(255) DEFAULT NULL,
  `correct_option` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `questions`
--

INSERT INTO `questions` (`id`, `subject_id`, `question_text`, `option1`, `option2`, `option3`, `option4`, `correct_option`) VALUES
(3, 11, 'full form of RDBMS', 'real database management system', 'relational database management system', 'relation database management system', 'none', 2),
(4, 11, 'SQL stands for ______________', 'structured query language', 'standard query language', 'sequential query language', 'server queue language', 1),
(5, 11, 'Which of the following sql command is classified as DDL command?', 'INSERT', 'UPDATE', 'GRANT', 'CREATE', 4),
(6, 11, 'A table is in 3rd normal form if it is in 2NF and has no:', 'Repeating groups', 'Partial functional dependencies', 'Transitive functional dependencies', 'Multi-valued dependencies', 3),
(7, 11, 'ACID stands for', 'Atomicity', 'Consistency', 'Isolation,Duarability', 'All of Above', 4),
(8, 11, 'which ACID property ensures that concurrent transactions do not  interference with each other\'s execution?', 'Atomicity', 'Consistency', 'Isolation', 'Durability', 3),
(9, 11, 'in relational database ,data is stored structurally inside which of the following ?', 'tables', 'text files', 'folders', 'arrays', 1),
(11, 11, 'What is Python?', 'Language', 'Animal', 'Car', 'Book', 1),
(12, 11, 'HTML stands for?', 'Hyper Text Markup Language', 'Home Tool', 'Hyper Tool', '', 1);

-- --------------------------------------------------------

--
-- Table structure for table `results`
--

CREATE TABLE `results` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `subject_id` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `total_questions` int(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `exam_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `results`
--

INSERT INTO `results` (`id`, `user_id`, `subject_id`, `score`, `total_questions`, `status`, `exam_date`) VALUES
(1, 2, 1, 1, 1, 'PASS', '2026-07-22 16:19:33'),
(2, 2, 2, 1, 1, 'PASS', '2026-07-22 16:29:07'),
(3, 2, 2, 0, 1, 'FAIL', '2026-07-22 16:47:14'),
(4, 2, 2, 1, 1, 'PASS', '2026-07-22 16:50:04'),
(5, 2, 2, 0, 1, 'FAIL', '2026-07-22 17:09:55'),
(8, 2, 11, 1, 1, 'PASS', '2026-07-24 16:49:39'),
(9, 3, 11, 0, 1, 'FAIL', '2026-07-24 16:57:24'),
(10, 3, 11, 0, 1, 'FAIL', '2026-07-24 17:08:46'),
(11, 3, 11, 0, 1, 'FAIL', '2026-07-24 17:49:46'),
(12, 3, 11, 0, 1, 'FAIL', '2026-07-24 17:50:42'),
(13, 3, 11, 0, 1, 'FAIL', '2026-07-24 17:54:58'),
(14, 3, 11, 1, 1, 'PASS', '2026-07-24 17:55:13'),
(15, 3, 11, 1, 1, 'PASS', '2026-07-24 17:56:56'),
(16, 2, 11, 0, 1, 'FAIL', '2026-07-24 18:03:51'),
(17, 2, 11, 1, 1, 'PASS', '2026-07-24 18:04:05'),
(18, 5, 11, 1, 1, 'PASS', '2026-07-24 18:41:28'),
(19, 2, 11, 1, 1, 'PASS', '2026-07-25 10:51:38'),
(20, 5, 11, 1, 1, 'PASS', '2026-07-25 10:58:21'),
(21, 5, 11, 0, 1, 'FAIL', '2026-07-25 10:59:05'),
(22, 5, 11, 1, 1, 'PASS', '2026-07-25 11:00:35'),
(23, 5, 11, 1, 1, 'PASS', '2026-07-25 11:01:08'),
(24, 5, 11, 1, 1, 'PASS', '2026-07-25 11:08:40'),
(25, 5, 11, 0, 1, 'FAIL', '2026-07-25 11:08:57'),
(26, 5, 11, 3, 7, 'PASS', '2026-07-25 11:33:56'),
(27, 5, 11, 2, 7, 'FAIL', '2026-07-25 11:39:32'),
(28, 5, 11, 5, 7, 'PASS', '2026-07-25 11:58:45'),
(29, 5, 11, 3, 7, 'PASS', '2026-07-25 13:01:23'),
(30, 5, 11, 7, 7, 'PASS', '2026-07-25 16:01:32'),
(31, 5, 11, 6, 7, 'PASS', '2026-07-25 16:48:11'),
(32, 5, 11, 4, 7, 'PASS', '2026-07-25 17:00:31'),
(37, 5, 11, 9, 9, 'PASS', '2026-07-25 18:58:03'),
(38, 5, 11, 7, 9, 'PASS', '2026-07-26 11:05:47'),
(39, 6, 11, 9, 9, 'PASS', '2026-07-26 11:13:26'),
(40, 6, 11, 7, 9, 'PASS', '2026-07-26 12:21:20'),
(41, 6, 11, 7, 9, 'PASS', '2026-07-26 12:32:53'),
(42, 5, 11, 9, 9, 'PASS', '2026-07-26 12:37:52'),
(43, 5, 11, 8, 9, 'PASS', '2026-07-26 12:47:12'),
(44, 5, 11, 9, 9, 'PASS', '2026-07-26 12:53:00'),
(45, 5, 11, 5, 9, 'PASS', '2026-07-26 13:15:48'),
(46, 7, 11, 8, 9, 'PASS', '2026-07-27 08:46:42'),
(47, 7, 11, 8, 9, 'PASS', '2026-07-27 08:50:08'),
(48, 7, 11, 8, 9, 'PASS', '2026-07-27 08:50:18'),
(49, 7, 11, 8, 9, 'PASS', '2026-07-27 08:50:29'),
(50, 7, 11, 9, 9, 'PASS', '2026-07-27 08:51:53'),
(51, 7, 11, 9, 9, 'PASS', '2026-07-27 08:54:15'),
(52, 7, 11, 9, 9, 'PASS', '2026-07-27 08:59:46'),
(53, 7, 11, 9, 9, 'PASS', '2026-07-27 09:02:40'),
(54, 7, 11, 9, 9, 'PASS', '2026-07-27 09:03:10'),
(55, 5, 11, 5, 9, 'PASS', '2026-07-29 05:29:59'),
(56, 5, 11, 5, 9, 'PASS', '2026-07-29 05:30:22'),
(57, 5, 11, 5, 9, 'PASS', '2026-07-29 05:35:43'),
(58, 5, 11, 8, 9, 'PASS', '2026-07-29 05:48:07'),
(59, 5, 11, 8, 9, 'PASS', '2026-07-29 06:01:15'),
(61, 5, 11, 8, 9, 'PASS', '2026-07-29 06:12:37'),
(62, 5, 11, 8, 9, 'PASS', '2026-07-29 06:13:43'),
(63, 5, 11, 8, 9, 'PASS', '2026-07-29 06:14:58'),
(64, 5, 11, 8, 9, 'PASS', '2026-07-29 06:15:34'),
(65, 5, 11, 8, 9, 'PASS', '2026-07-29 06:53:00'),
(66, 5, 11, 8, 9, 'PASS', '2026-07-29 07:10:45'),
(67, 5, 11, 7, 9, 'PASS', '2026-07-29 07:11:35'),
(69, 10, 11, 7, 9, 'PASS', '2026-09-11 19:03:22'),
(70, 10, 11, 0, 9, 'FAIL', '2026-09-11 19:36:54'),
(71, 10, 11, 8, 9, 'PASS', '2026-09-11 20:04:40'),
(72, 10, 11, 0, 9, 'FAIL', '2026-09-11 21:12:48'),
(73, 10, 11, 0, 9, 'FAIL', '2026-09-11 21:13:45'),
(74, 10, 11, 0, 9, 'FAIL', '2026-09-11 21:14:29'),
(75, 10, 11, 0, 9, 'FAIL', '2026-09-11 21:15:09'),
(76, 11, 11, 3, 9, 'FAIL', '2026-09-12 04:18:48'),
(77, 12, 11, 7, 9, 'PASS', '2026-09-12 04:24:03'),
(78, 16, 11, 8, 9, 'PASS', '2026-10-04 17:38:33');

-- --------------------------------------------------------

--
-- Table structure for table `student_exam`
--

CREATE TABLE `student_exam` (
  `attempt_id` int(11) NOT NULL,
  `student_id` int(11) DEFAULT NULL,
  `exam_id` int(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `total_questions` int(11) DEFAULT 0,
  `attempted_questions` int(11) DEFAULT 0,
  `correct_answers` int(11) DEFAULT 0,
  `wrong_answers` int(11) DEFAULT 0,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `submitted_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `student_exam`
--

INSERT INTO `student_exam` (`attempt_id`, `student_id`, `exam_id`, `status`, `score`, `total_questions`, `attempted_questions`, `correct_answers`, `wrong_answers`, `start_time`, `end_time`, `submitted_at`) VALUES
(1, 2, 1, 'Started', 0, 0, 0, 0, 0, NULL, NULL, NULL),
(2, 2, 1, 'Completed', 1, 0, 0, 0, 0, NULL, NULL, NULL),
(3, 3, 1, 'Completed', 0, 0, 0, 0, 0, NULL, NULL, NULL),
(4, 3, 1, 'Completed', 0, 0, 0, 0, 0, NULL, NULL, NULL),
(5, 3, 1, 'Completed', 0, 0, 0, 0, 0, NULL, NULL, NULL),
(6, 3, 1, 'Completed', 1, 0, 0, 0, 0, NULL, NULL, NULL),
(7, 3, 1, 'Completed', 1, 0, 0, 0, 0, NULL, NULL, NULL),
(8, 3, 1, 'Started', 0, 0, 0, 0, 0, NULL, NULL, NULL),
(9, 2, 1, 'Completed', 0, 0, 0, 0, 0, NULL, NULL, NULL),
(10, 2, 1, 'Completed', 1, 0, 0, 0, 0, NULL, NULL, NULL),
(11, 5, 1, 'Completed', 1, 0, 0, 0, 0, NULL, NULL, NULL),
(12, 2, 1, 'Completed', 1, 1, 1, 1, 0, '2026-07-25 16:21:29', '2026-07-25 16:21:38', '2026-07-25 16:21:38'),
(13, 5, 1, 'Completed', 1, 1, 1, 1, 0, '2026-07-25 16:28:11', '2026-07-25 16:28:21', '2026-07-25 16:28:21'),
(14, 5, 1, 'Completed', 0, 1, 1, 0, 1, '2026-07-25 16:28:53', '2026-07-25 16:29:05', '2026-07-25 16:29:05'),
(15, 5, 1, 'Completed', 1, 1, 1, 1, 0, '2026-07-25 16:30:23', '2026-07-25 16:30:35', '2026-07-25 16:30:35'),
(16, 5, 1, 'Completed', 1, 1, 1, 1, 0, '2026-07-25 16:30:59', '2026-07-25 16:31:08', '2026-07-25 16:31:08'),
(17, 5, 1, 'Completed', 1, 1, 1, 1, 0, '2026-07-25 16:38:30', '2026-07-25 16:38:40', '2026-07-25 16:38:40'),
(18, 5, 1, 'Completed', 0, 1, 1, 0, 1, '2026-07-25 16:38:49', '2026-07-25 16:38:57', '2026-07-25 16:38:57'),
(19, 5, 1, 'Started', 0, 0, 0, 0, 0, '2026-07-25 16:48:45', NULL, NULL),
(20, 5, 1, 'Completed', 3, 7, 7, 4, 3, '2026-07-25 17:03:18', '2026-07-25 17:03:56', '2026-07-25 17:03:56'),
(21, 5, 1, 'Completed', 2, 7, 7, 3, 4, '2026-07-25 17:08:39', '2026-07-25 17:09:32', '2026-07-25 17:09:32'),
(22, 5, 1, 'Completed', 4.5, 7, 7, 5, 2, '2026-07-25 17:28:04', '2026-07-25 17:28:45', '2026-07-25 17:28:45'),
(23, 5, 1, 'Completed', 3.25, 7, 7, 4, 3, '2026-07-25 18:30:55', '2026-07-25 18:31:23', '2026-07-25 18:31:23'),
(24, 5, 1, 'Completed', 7, 7, 7, 7, 0, '2026-07-25 21:30:22', '2026-07-25 21:31:32', '2026-07-25 21:31:32'),
(25, 5, 1, 'Completed', 5.75, 7, 7, 6, 1, '2026-07-25 22:17:40', '2026-07-25 22:18:11', '2026-07-25 22:18:11'),
(26, 5, 1, 'Completed', 3.5, 7, 6, 4, 2, '2026-07-25 22:29:46', '2026-07-25 22:30:31', '2026-07-25 22:30:31'),
(27, 5, 1, 'Started', 0, 0, 0, 0, 0, '2026-07-26 00:11:10', NULL, NULL),
(28, 5, 1, 'Completed', 9, 9, 9, 9, 0, '2026-07-26 00:27:17', '2026-07-26 00:28:03', '2026-07-26 00:28:03'),
(29, 5, 1, 'Completed', 6.5, 9, 9, 7, 2, '2026-07-26 16:34:46', '2026-07-26 16:35:47', '2026-07-26 16:35:47'),
(30, 6, 1, 'Completed', 9, 9, 9, 9, 0, '2026-07-26 16:40:55', '2026-07-26 16:43:26', '2026-07-26 16:43:26'),
(31, 6, 1, 'Completed', 6.75, 9, 8, 7, 1, '2026-07-26 17:50:48', '2026-07-26 18:02:53', '2026-07-26 18:02:53'),
(32, 5, 1, 'Completed', 9, 9, 9, 9, 0, '2026-07-26 18:07:09', '2026-07-26 18:07:52', '2026-07-26 18:07:52'),
(33, 5, 1, 'Completed', 7.75, 9, 9, 8, 1, '2026-07-26 18:16:39', '2026-07-26 18:17:12', '2026-07-26 18:17:12'),
(34, 5, 1, 'Completed', 9, 9, 9, 9, 0, '2026-07-26 18:22:28', '2026-07-26 18:23:00', '2026-07-26 18:23:00'),
(35, 5, 1, 'Completed', 5.25, 9, 9, 6, 3, '2026-07-26 18:45:04', '2026-07-26 18:45:48', '2026-07-26 18:45:48'),
(36, 5, 1, 'Started', 0, 0, 0, 0, 0, '2026-07-26 22:15:55', NULL, NULL),
(37, 5, 1, 'Started', 0, 0, 0, 0, 0, '2026-07-26 23:06:11', NULL, NULL),
(38, 7, 1, 'Completed', 9, 9, 9, 9, 0, '2026-07-27 14:15:58', '2026-07-27 14:24:15', '2026-07-27 14:24:15'),
(39, 7, 1, 'Completed', 9, 9, 9, 9, 0, '2026-07-27 14:29:13', '2026-07-27 14:33:10', '2026-07-27 14:33:10'),
(40, 5, 1, 'Started', 0, 0, 0, 0, 0, '2026-07-27 20:54:34', NULL, NULL),
(41, 5, 1, 'Started', 0, 0, 0, 0, 0, '2026-07-27 20:54:49', NULL, NULL),
(42, 5, 1, 'Completed', 5, 9, 5, 5, 0, '2026-07-29 10:59:21', '2026-07-29 11:05:43', '2026-07-29 11:05:43'),
(43, 5, 1, 'Completed', 7.75, 9, 9, 8, 1, '2026-07-29 11:17:37', '2026-07-29 11:43:43', '2026-07-29 11:43:43'),
(44, 5, 1, 'Completed', 7.75, 9, 9, 8, 1, '2026-07-29 11:44:23', '2026-07-29 11:45:34', '2026-07-29 11:45:34'),
(45, 5, 1, 'Completed', 6.5, 9, 9, 7, 2, '2026-07-29 12:22:32', '2026-07-29 12:41:35', '2026-07-29 12:41:35'),
(46, 10, 1, 'Started', 0, 0, 0, 0, 0, '2026-09-11 21:23:29', NULL, NULL),
(47, 10, 1, 'Started', 0, 0, 0, 0, 0, '2026-09-11 21:41:13', NULL, NULL),
(48, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-11 23:00:08', NULL, NULL),
(49, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-11 23:29:28', NULL, NULL),
(50, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-11 23:30:45', NULL, NULL),
(51, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-11 23:31:25', NULL, NULL),
(52, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-11 23:32:42', NULL, NULL),
(53, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-12 00:13:02', NULL, NULL),
(54, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-12 00:19:10', NULL, NULL),
(55, 10, 1, 'Completed', 7, 0, 0, 0, 0, NULL, NULL, NULL),
(56, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-12 00:48:11', NULL, NULL),
(57, 10, 1, 'Completed', 0, 9, 0, 0, 0, '2026-09-12 01:05:58', '2026-09-12 01:06:54', '2026-09-12 01:06:54'),
(58, 10, 1, 'Completed', 7.8, 9, 9, 8, 1, '2026-09-12 01:33:43', '2026-09-12 01:34:40', '2026-09-12 01:34:40'),
(59, 10, 1, 'started', NULL, 9, 0, 0, 0, '2026-09-12 02:01:01', NULL, NULL),
(60, 10, 1, 'Completed', 0, 9, 0, 0, 0, '2026-09-12 02:42:18', '2026-09-12 02:42:48', '2026-09-12 02:42:48'),
(61, 10, 1, 'Completed', 0, 9, 0, 0, 0, '2026-09-12 02:43:30', '2026-09-12 02:43:45', '2026-09-12 02:43:45'),
(62, 10, 1, 'Completed', 0, 9, 0, 0, 0, '2026-09-12 02:43:56', '2026-09-12 02:44:29', '2026-09-12 02:44:29'),
(63, 10, 1, 'Completed', 0, 9, 0, 0, 0, '2026-09-12 02:44:47', '2026-09-12 02:45:09', '2026-09-12 02:45:09'),
(64, 11, 1, 'Completed', 2.8, 9, 9, 4, 5, '2026-09-12 09:47:52', '2026-09-12 09:48:48', '2026-09-12 09:48:48'),
(65, 12, 1, 'Completed', 6.5, 9, 9, 7, 2, '2026-09-12 09:52:50', '2026-09-12 09:54:03', '2026-09-12 09:54:03'),
(66, 16, 1, 'Completed', 7.8, 9, 9, 8, 1, '2026-10-04 23:07:21', '2026-10-04 23:08:33', '2026-10-04 23:08:33');

-- --------------------------------------------------------

--
-- Table structure for table `subjects`
--

CREATE TABLE `subjects` (
  `id` int(11) NOT NULL,
  `subject_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `subjects`
--

INSERT INTO `subjects` (`id`, `subject_name`) VALUES
(11, 'RDBMS');

-- --------------------------------------------------------

--
-- Table structure for table `test_history`
--

CREATE TABLE `test_history` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `attempt_id` int(11) NOT NULL,
  `test_date` date DEFAULT NULL,
  `subject_name` varchar(50) DEFAULT NULL,
  `band_score` decimal(3,1) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `test_history`
--

INSERT INTO `test_history` (`id`, `student_id`, `attempt_id`, `test_date`, `subject_name`, `band_score`, `status`) VALUES
(1, 0, 0, '2026-07-24', 'RDBMS', 9.0, 'Completed'),
(2, 0, 0, '2026-07-24', 'RDBMS', 0.0, 'Completed'),
(3, 0, 0, '2026-07-24', 'RDBMS', 0.0, 'Completed'),
(4, 3, 0, '2026-07-24', 'RDBMS', 0.0, 'Completed'),
(5, 3, 0, '2026-07-24', 'RDBMS', 9.0, 'Completed'),
(6, 3, 0, '2026-07-24', 'RDBMS', 9.0, 'Completed'),
(7, 2, 0, '2026-07-24', 'RDBMS', 0.0, 'Completed'),
(8, 2, 0, '2026-07-24', 'RDBMS', 9.0, 'Completed'),
(9, 5, 0, '2026-07-25', 'RDBMS', 9.0, 'Completed'),
(10, 2, 0, '2026-07-25', 'RDBMS', 9.0, 'Completed'),
(11, 5, 0, '2026-07-25', 'RDBMS', 9.0, 'Completed'),
(12, 5, 0, '2026-07-25', 'RDBMS', 0.0, 'Completed'),
(13, 5, 0, '2026-07-25', 'RDBMS', 9.0, 'Completed'),
(14, 5, 0, '2026-07-25', 'RDBMS', 9.0, 'Completed'),
(15, 5, 17, '2026-07-25', 'RDBMS', 9.0, 'Completed'),
(16, 5, 18, '2026-07-25', 'RDBMS', 0.0, 'Completed'),
(17, 5, 20, '2026-07-25', 'RDBMS', 4.2, 'Completed'),
(18, 5, 21, '2026-07-25', 'RDBMS', 2.6, 'Completed'),
(19, 5, 22, '2026-07-25', 'RDBMS', 5.8, 'Completed'),
(20, 5, 23, '2026-07-25', 'RDBMS', 4.2, 'Completed'),
(21, 5, 24, '2026-07-25', 'RDBMS', 9.0, 'Completed'),
(22, 5, 25, '2026-07-25', 'RDBMS', 7.4, 'Completed'),
(23, 5, 26, '2026-07-25', 'RDBMS', 4.5, 'Completed'),
(28, 5, 28, '2026-07-26', 'RDBMS', 9.0, 'Completed'),
(29, 5, 29, '2026-07-26', 'RDBMS', 6.5, 'Completed'),
(30, 6, 30, '2026-07-26', 'RDBMS', 9.0, 'Completed'),
(31, 6, 31, '2026-07-26', 'RDBMS', 6.8, 'Completed'),
(32, 6, 31, '2026-07-26', 'RDBMS', 6.8, 'Completed'),
(33, 5, 32, '2026-07-26', 'RDBMS', 9.0, 'Completed'),
(34, 5, 33, '2026-07-26', 'RDBMS', 7.8, 'Completed'),
(35, 5, 34, '2026-07-26', 'RDBMS', 9.0, 'Completed'),
(36, 5, 35, '2026-07-26', 'RDBMS', 5.2, 'Completed'),
(37, 7, 38, '2026-07-27', 'RDBMS', 7.8, 'Completed'),
(38, 7, 38, '2026-07-27', 'RDBMS', 7.8, 'Completed'),
(39, 7, 38, '2026-07-27', 'RDBMS', 7.8, 'Completed'),
(40, 7, 38, '2026-07-27', 'RDBMS', 7.8, 'Completed'),
(41, 7, 38, '2026-07-27', 'RDBMS', 9.0, 'Completed'),
(42, 7, 38, '2026-07-27', 'RDBMS', 9.0, 'Completed'),
(43, 7, 39, '2026-07-27', 'RDBMS', 9.0, 'Completed'),
(44, 7, 39, '2026-07-27', 'RDBMS', 9.0, 'Completed'),
(45, 7, 39, '2026-07-27', 'RDBMS', 9.0, 'Completed'),
(46, 5, 42, '2026-07-29', 'RDBMS', 5.0, 'Completed'),
(47, 5, 42, '2026-07-29', 'RDBMS', 5.0, 'Completed'),
(48, 5, 42, '2026-07-29', 'RDBMS', 5.0, 'Completed'),
(49, 5, 43, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(50, 5, 43, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(52, 5, 43, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(53, 5, 43, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(54, 5, 44, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(55, 5, 44, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(56, 5, 45, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(57, 5, 45, '2026-07-29', 'RDBMS', 7.8, 'Completed'),
(58, 5, 45, '2026-07-29', 'RDBMS', 6.5, 'Completed'),
(60, 0, 0, '2026-09-12', 'RDBMS', 7.0, 'Completed'),
(61, 10, 57, '2026-09-12', 'RDBMS', 0.0, 'Completed'),
(62, 10, 58, '2026-09-12', 'RDBMS', 7.8, 'Completed'),
(63, 10, 60, '2026-09-12', 'RDBMS', 0.0, 'Completed'),
(64, 10, 61, '2026-09-12', 'RDBMS', 0.0, 'Completed'),
(65, 10, 62, '2026-09-12', 'RDBMS', 0.0, 'Completed'),
(66, 10, 63, '2026-09-12', 'RDBMS', 0.0, 'Completed'),
(67, 11, 64, '2026-09-12', 'RDBMS', 2.8, 'Completed'),
(68, 12, 65, '2026-09-12', 'RDBMS', 6.5, 'Completed'),
(69, 16, 66, '2026-10-04', 'RDBMS', 7.8, 'Completed');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `fullname` text NOT NULL,
  `username` text NOT NULL,
  `email` text NOT NULL,
  `mobile` int(10) NOT NULL,
  `password` text NOT NULL,
  `photo` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `fullname`, `username`, `email`, `mobile`, `password`, `photo`) VALUES
(2, 'vishva bhuva', 'vishu', 'vishu@gmail.com', 0, 'vishu', ''),
(3, 'rensi chovatiya', 'reni', 'reni@gmail.com', 0, 'reni123', ''),
(10, 'babariya manali', 'manali', 'manali112@gmail.com', 2147483647, 'manali123', 'manali.jpeg'),
(11, 'vekariya trushti', 'trushti', 'trushti@gmail.om', 2147483647, 'trushti', 'trushti.jpeg'),
(12, 'suva ', 'bhai', 'suvatushar6314@gmail.com', 2147483647, '9104913091', 'WIN_20260912_09_50_21_Pro.jpg'),
(16, 'hemanshi trivedi', 'hemu', 'hemu123@gmail.com', 2147483647, 'hemu12', 'hemu_c61fd559.jpeg');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `exams`
--
ALTER TABLE `exams`
  ADD PRIMARY KEY (`exam_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `questions`
--
ALTER TABLE `questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `subject_id` (`subject_id`);

--
-- Indexes for table `results`
--
ALTER TABLE `results`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `student_exam`
--
ALTER TABLE `student_exam`
  ADD PRIMARY KEY (`attempt_id`);

--
-- Indexes for table `subjects`
--
ALTER TABLE `subjects`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `subject_name` (`subject_name`);

--
-- Indexes for table `test_history`
--
ALTER TABLE `test_history`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`) USING HASH,
  ADD UNIQUE KEY `email` (`email`) USING HASH;

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `exams`
--
ALTER TABLE `exams`
  MODIFY `exam_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `questions`
--
ALTER TABLE `questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `results`
--
ALTER TABLE `results`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=79;

--
-- AUTO_INCREMENT for table `student_exam`
--
ALTER TABLE `student_exam`
  MODIFY `attempt_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=67;

--
-- AUTO_INCREMENT for table `subjects`
--
ALTER TABLE `subjects`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `test_history`
--
ALTER TABLE `test_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=70;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `questions`
--
ALTER TABLE `questions`
  ADD CONSTRAINT `questions_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
