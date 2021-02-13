#!/usr/bin/env python
# coding: utf-8

# Exploration of Various SQL Methods for Data Analytics

# ### Example Data:
# 
# Botanic Gardens Conservation International (BGCI)
# Plants Threat Assessment: https://tools.bgci.org/plant_search.php

import os
import sqlite3
import pandas as pd

cd = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(f"{cd}/data/BGCI_Plants_ThreatSearch.db")


# Data Organization
# (e.g., data ordering, cleaning, formatting, processing)

sql = """SELECT major_group
			  , family
			  , genus
			  , plant_name
			  , published_conservation_status AS published_status
			  , interpreted_conservation_status AS interpreted_status
			  , assessment_year
			  , scope
			  , source
		 FROM plants_assessment 
		 LIMIT 10;
      """

threat_plants_df = pd.read_sql(sql, conn)
print(threat_plants_df)


sql = """SELECT major_group
			  , family
			  , genus
			  , SUBSTR(plant_name, 1, INSTR(plant_name, ' '))                         -- STRING FUNCTIONS
				||              
				SUBSTR(REPLACE(plant_name,
				               SUBSTR(plant_name, 1, INSTR(plant_name, ' ')),
				               ''),
				       1, 
				       INSTR(REPLACE(plant_name,
				                     SUBSTR(plant_name, 1, INSTR(plant_name, ' ')),
				                    ''),
				             ' ')
				       ) AS plant       
			  , published_conservation_status AS published_status
			  , CASE                                                                  -- CONDITIONAL LOGIC
				    WHEN interpreted_conservation_status = 'Data Deficient'
				    THEN NULL
				    ELSE interpreted_conservation_status
				END AS interpreted_status
			  , assessment_year
			  , assessment_year - 1970 AS study_year                                  -- ARITHMETIC OPERATIONS
			  , CASE                                                                  -- CONDITIONAL LOGIC
				    WHEN scope LIKE '%Unknown%'                                       -- STRING PATTERN SEARCH
				    THEN NULL
				    ELSE scope                                                      
				END AS scope
			  , SUBSTR(source, 1, 30) AS short_source                                 -- STRING FUNCTIONS  
				
		 FROM plants_assessment 
		 ORDER BY ROWID DESC LIMIT 10;
      """

threat_plants_df = pd.read_sql(sql, conn)
print(threat_plants_df)


# Set-Based Operations
# (e.g., group/clusters or sampling representation)

sql = """SELECT scope
		 FROM plants_assessment
		 WHERE interpreted_conservation_status = 'Not Threatened'
		 GROUP BY scope

		 UNION 

		 SELECT scope
		 FROM plants_assessment
		 WHERE interpreted_conservation_status = 'Threatened'
		 GROUP BY scope
      """

union_df = pd.read_sql(sql, conn)
print(union_df)

sql = """SELECT scope
		 FROM plants_assessment
		 WHERE interpreted_conservation_status = 'Not Threatened'
		 GROUP BY scope

		 INTERSECT

		 SELECT scope
		 FROM plants_assessment
		 WHERE interpreted_conservation_status = 'Threatened'
		 GROUP BY scope
      """

intersect_df = pd.read_sql(sql, conn)
print(intersect_df)

sql = """SELECT scope
         FROM plants_assessment
		 WHERE interpreted_conservation_status = 'Threatened'
		 GROUP BY scope

		 EXCEPT

		 SELECT scope
		 FROM plants_assessment
		 WHERE interpreted_conservation_status = 'Not Threatened'
		 GROUP BY scope
      """

except_df = pd.read_sql(sql, conn)
print(except_df)


# Combinations/Permutations Pairing
# (e.g., balanced longitudinal panel and time series)

sql = """SELECT m.major_group
			  , y.assessment_year
		 FROM 
		   (SELECT DISTINCT major_group FROM plants_assessment) m
		 CROSS JOIN
		   (SELECT DISTINCT assessment_year FROM plants_assessment) y
		 WHERE m.major_group IS NOT NULL
		   AND y.assessment_year IS NOT NULL
		 ORDER BY m.major_group
		  	    , y.assessment_year
      """

combn_df = pd.read_sql(sql, conn)
print(combn_df)


# Aggregation
# (e.g., summary stats and diagnostics)

# By One Group
sql = """SELECT p.major_group
		 	  , COUNT(DISTINCT p.family) AS unq_families
			  , COUNT(DISTINCT p.genus) AS unq_genera
			  , COUNT(p.plant_name) AS count_plants
			  , MIN(p.assessment_year) AS min_year
			  , MAX(p.assessment_year) AS max_year
			 
		 FROM plants_assessment p
		 GROUP BY p.major_group
      """

agg_df = pd.read_sql(sql, conn)
print(agg_df)


sql = """SELECT p.interpreted_conservation_status
		 	  , COUNT(DISTINCT p.family) AS unq_families
			  , COUNT(DISTINCT p.genus) AS unq_genera
			  , COUNT(p.plant_name) AS count_pants
			  , MIN(p.assessment_year) AS min_year
			  , MAX(p.assessment_year) AS max_year
			 
		 FROM plants_assessment p
		 GROUP BY p.interpreted_conservation_status
      """

agg_df = pd.read_sql(sql, conn)
print(agg_df)


# By Multiple Groups
sql = """SELECT p.major_group
			  , p.interpreted_conservation_status
			  , COUNT(DISTINCT p.family) AS unq_families
			  , COUNT(DISTINCT p.genus) AS unq_genera
			  , COUNT(p.plant_name) AS count_plants
			  , MIN(p.assessment_year) AS min_year
			  , MAX(p.assessment_year) AS max_year
			 
		 FROM plants_assessment p
		 GROUP BY p.major_group
		 	    , p.interpreted_conservation_status
      """

agg_df = pd.read_sql(sql, conn)
print(agg_df)



# Reshape Data
# (e.g., reporting/presentation)

sql = """SELECT p.major_group
			  , SUM(p.assessment_year == 2015) AS count_plants_2015
			  , SUM(p.assessment_year == 2016) AS count_plants_2016
			  , SUM(p.assessment_year == 2017) AS count_plants_2017
			  , SUM(p.assessment_year == 2018) AS count_plants_2018
			  , SUM(p.assessment_year == 2019) AS count_plants_2019
			  , SUM(p.assessment_year == 2020) AS count_plants_2020
		 FROM plants_assessment p
		 WHERE p.interpreted_conservation_status = 'Threatened' 
		 GROUP BY p.major_group
      """

wide_df = pd.read_sql(sql, conn)
print(wide_df)


sql = """SELECT p.major_group
			  , COUNT(*) AS count_plants
			  , SUM(p.interpreted_conservation_status = 'Threatened') AS count_threatened_plants
			  , SUM(p.interpreted_conservation_status = 'Not Threatened') AS count_not_threatened_plants
		 FROM plants_assessment p
		 WHERE p.assessment_year >= 2015
		 GROUP BY p.major_group
      """

wide_df = pd.read_sql(sql, conn)
print(wide_df)


# Common Table Expression (CTE) And Window Functions
# (e.g., running calculations, lead/lag variables, moving averages)

sql = """WITH sub AS 
		   (SELECT p.major_group
			     , p.interpreted_conservation_status
			     , COUNT(DISTINCT p.family) AS unq_families
			     , COUNT(DISTINCT p.genus) AS unq_genera
			     , COUNT(p.plant_name)*1.00 AS count_plants
			     , MIN(p.assessment_year) AS min_year
			     , MAX(p.assessment_year) AS max_year
		    FROM plants_assessment p
		    GROUP BY p.major_group
			  	   , p.interpreted_conservation_status
		   ) 
		  
		 SELECT sub.major_group
		  	  , sub.interpreted_conservation_status
			  , sub.count_plants
			  , ROW_NUMBER() OVER(PARTITION BY sub.major_group
			 	                  ORDER BY sub.count_plants DESC) AS rn
			  , SUM(sub.count_plants) OVER(PARTITION BY sub.major_group) AS group_sum
			  , ROUND(sub.count_plants / SUM(sub.count_plants) 
				                             OVER(PARTITION BY sub.major_group), 4) * 100 AS pct_total
			  , SUM(sub.count_plants) OVER(PARTITION BY sub.major_group
				                           ORDER BY sub.count_plants DESC) AS run_sum
		 FROM sub
		 ORDER BY sub.major_group
		  	    , sub.count_plants DESC
      """

cte_df = pd.read_sql(sql, conn)
print(cte_df)


# Interval, Lateral, and Range Join
# (e.g., log files, event/time studies, tracking data)

sql = """WITH sub AS 
		   (SELECT p.major_group
			     , p.assessment_year
			     , COUNT(DISTINCT p.family) AS unq_families
			     , COUNT(DISTINCT p.genus) AS unq_genera
			     , COUNT(p.plant_name)*1.00 AS count_plants
			     , MIN(p.assessment_year) AS min_year
			     , MAX(p.assessment_year) AS max_year
		    FROM plants_assessment p
		    WHERE p.interpreted_conservation_status = 'Threatened' 
		    GROUP BY p.major_group
			 	   , p.assessment_year
		   ) 
		  
		 SELECT s1.major_group
			  , s1.assessment_year AS year1
			  , s2.assessment_year AS year2
			  , s1.count_plants AS count_plants_y1
			  , s2.count_plants AS count_plants_y2
			  , ROUND((s2.count_plants - s1.count_plants) / s2.count_plants, 2) AS year_pct_change
		 FROM sub s1
		 INNER JOIN sub  s2
		    ON s1.major_group = s2.major_group 
		   AND s1.assessment_year = (s2.assessment_year - 1)
		 ORDER BY s1.major_group
		  	    , s1.assessment_year DESC
			    , s2.assessment_year DESC
      """

interval_df = pd.read_sql(sql, conn)
print(interval_df)


