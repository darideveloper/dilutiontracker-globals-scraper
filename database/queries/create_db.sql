CREATE TABLE `new_filings` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `ticker` varchar(5),
  `company_name` varchar(100),
  `dilution_type` varchar(50),
  `dilution_name` varchar(50),
  `date_modified` date,
  `query_date` date
);

CREATE TABLE `completed_offerings` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `ticker` varchar(5),
  `type` varchar(50),
  `method` varchar(5),
  `share_equivalent` bigint,
  `price` float,
  `warrants` bigint,
  `offering_amt` bigint,
  `bank` varchar(50),
  `investors` varchar(50),
  `datetime` date,
  `query_date` date
);

CREATE TABLE `pending_s1s` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `ticker` varchar(5),
  `company_name` varchar(50),
  `industry` varchar(50),
  `date_first_s1` date,
  `pricing_date` date,
  `anticipated_deal_size` varchar(20),
  `estimated_warrant_coverage` int,
  `underwriters_placement_agents` varchar(20),
  `float_before_offering` bigint,
  `status` varchar(20),
  `pricing` float,
  `shares_offered` bigint,
  `final_warrant_coverage` int,
  `exercise_price` float,
  `query_date` date
);

CREATE TABLE `reverse_splits` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `symbol` varchar(5),
  `effective_date` date,
  `split_ratio` varchar(15),
  `current_float_m` float,
  `status` varchar(20),
  `query_date` date
);

CREATE TABLE `noncompliant` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `ticker` varchar(20),
  `company` varchar(200),
  `deficiency` varchar(50),
  `market` varchar(5),
  `notification_date` date,
  `query_date` date
);
