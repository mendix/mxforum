-- phpMyAdmin SQL Dump
-- version 3.0.0-beta
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 12, 2009 at 08:55 PM
-- Server version: 5.0.67
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `twogeekt_lanai`
--

--
-- Dumping data for table `badge`
--

INSERT INTO `badge` (`id`, `name`, `type`, `slug`, `description`, `multiple`, `awarded_count`) VALUES
(1, 'Purgatory Master', 3, 'Purgatory Master', '3 delete their posts in favor of the above', 1, 0),
(2, 'Pressure on white-collar', 3, 'Pressure on white-collar', 'Delete their own against more than 3 posts', 1, 0),
(3, 'Excellent answer', 3, 'Excellent answer', 'Answer well more than 10', 1, 0),
(4, 'Outstanding issues', 3, 'Outstanding issues', 'Issues received more than 10', 1, 0),
(5, 'Critics', 3, 'Critics', 'More than 10 comments', 1, 0),
(6, 'Epidemic', 3, 'Epidemic', 'Views the issue of more than 1000 views', 1, 0),
(7, 'Patrouille', 3, 'Patrouille', 'Spam messages marked the first time', 1, 0),
(8, 'Cleaners', 3, 'Cleaners', 'Revocation of the first to vote', 1, 0),
(9, 'Critics', 3, 'Critics', 'The first time against', 1, 0),
(10, 'Ambitious', 3, 'Ambitious', 'Edit to update the first time', 1, 0),
(11, 'Village', 3, 'Village', 'The first re-label', 1, 0),
(12, 'Scholars', 3, 'Scholars', 'Marking the first time the answer', 1, 0),
(13, 'Students', 3, 'Students', 'And the first question more than once in favor of', 1, 0),
(14, 'Supporters', 3, 'Supporters', 'The first time in favor of', 1, 0),
(15, 'Teachers', 3, 'Teachers', 'The first time to answer questions and receive more than one in favor of', 1, 0),
(16, 'Author Autobiography', 3, 'Autobiography, the author, complete information on all the options the user', 1, 0),
(17, 'Self-taught', 3, 'Self-taught', 'Answer their own problems and there is more than three in favor of', 1, 0),
(18, 'To answer the most valuable', 1, 'To answer the most valuable', 'Answered more than 100 times in favor of', 1, 0),
(19, 'The question of the most valuable', 1, 'The question of the most valuable', 'The issue of more than 100 times in favor of', 1, 0),
(20, 'David', 1, 'David', 'The problem is more than 100 collections', 1, 0),
(21, 'Well-known problem', 1, 'Well-known problem', 'Views the issue of more than 10,000 views', 1, 0),
(22, 'alpha users', 2, 'alpha users', 'Least one period of active users', 1, 0),
(23, 'Excellent answer', 2, 'Excellent answer', 'Answered more than 25 times in favor of', 1, 0),
(24, 'Excellent problem', 2, 'Excellent problem', 'More than 25 times in favor of the question', 1, 0),
(25, 'Popular issues', 2, 'Popular issues', 'The problem is more than 25 collections', 1, 0),
(26, 'Outstanding public', 2, 'Outstanding public', 'Voting for more than 300', 1, 0),
(27, 'Editorial director', 2, 'Editorial director', 'Edited 100 posts', 1, 0),
(28, 'Generalist', 2, 'Generalist', 'Active in a number of labels', 1, 0),
(29, 'Experts', 2, 'Experts', 'Active in the area of a label well', 1, 0),
(30, 'Long active', 2, 'Long active', 'More than one year of active users', 1, 0),
(31, 'Most concern', 2, 'Most concern', 'Views the issue of more than 2500 views', 1, 0),
(32, 'Scholars', 2, 'Scholars', 'The first answer was voted for more than 10', 1, 0),
(33, 'beta users', 2, 'beta users', 'Active participation during the beta', 1, 0),
(34, 'Instructor', 2, 'Instructor', 'Was designated as the best answer and in favor of more than 40', 1, 0),
(35, 'Wizards', 2, 'Wizards', 'After 60 days in question and answer in favor of more than 5', 1, 0),
(36, 'Category Expert', 2, 'Category expert', 'Tags have been created over the issue of the use of 50', 1, 0);
