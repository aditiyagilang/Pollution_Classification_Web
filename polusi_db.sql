-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 25, 2024 at 03:25 AM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `polusi_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `data_polusi`
--

CREATE TABLE `data_polusi` (
  `data_id` int NOT NULL,
  `esp_id` varchar(10) NOT NULL,
  `pm10` float NOT NULL,
  `pm25` float NOT NULL,
  `co` float NOT NULL,
  `hc` float NOT NULL,
  `o3` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `data_polusi`
--

INSERT INTO `data_polusi` (`data_id`, `esp_id`, `pm10`, `pm25`, `co`, `hc`, `o3`) VALUES
(2, 'ESP001', 56.7, 35.2, 0.9, 0.1, 0.07);

-- --------------------------------------------------------

--
-- Table structure for table `esp`
--

CREATE TABLE `esp` (
  `esp_id` varchar(10) NOT NULL,
  `location` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `esp`
--

INSERT INTO `esp` (`esp_id`, `location`) VALUES
('ESP001', 'Bojong gede');

-- --------------------------------------------------------

--
-- Table structure for table `ispu_data`
--

CREATE TABLE `ispu_data` (
  `ispu_id` int NOT NULL,
  `polusi_id` int NOT NULL,
  `ispu_pm10` float NOT NULL,
  `ispu_pm25` float NOT NULL,
  `ispu_co` float NOT NULL,
  `ispu_hc` float NOT NULL,
  `ispu_o3` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `ispu_data`
--

INSERT INTO `ispu_data` (`ispu_id`, `polusi_id`, `ispu_pm10`, `ispu_pm25`, `ispu_co`, `ispu_hc`, `ispu_o3`) VALUES
(1, 2, 78.5, 50.1, 3.2, 1.1, 2.3);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `data_polusi`
--
ALTER TABLE `data_polusi`
  ADD PRIMARY KEY (`data_id`),
  ADD KEY `esp_id` (`esp_id`);

--
-- Indexes for table `esp`
--
ALTER TABLE `esp`
  ADD PRIMARY KEY (`esp_id`);

--
-- Indexes for table `ispu_data`
--
ALTER TABLE `ispu_data`
  ADD PRIMARY KEY (`ispu_id`),
  ADD KEY `polusi_id` (`polusi_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `data_polusi`
--
ALTER TABLE `data_polusi`
  MODIFY `data_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `ispu_data`
--
ALTER TABLE `ispu_data`
  MODIFY `ispu_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `data_polusi`
--
ALTER TABLE `data_polusi`
  ADD CONSTRAINT `data_polusi_ibfk_1` FOREIGN KEY (`esp_id`) REFERENCES `esp` (`esp_id`);

--
-- Constraints for table `ispu_data`
--
ALTER TABLE `ispu_data`
  ADD CONSTRAINT `ispu_data_ibfk_1` FOREIGN KEY (`polusi_id`) REFERENCES `data_polusi` (`data_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
