#!/usr/bin/env Rscript

## Short Primer on how to work with nested data structures (XML and JSON) in R

#################
### XML Data
#################

## Example data uses Chicago CTA 'L' Rides Average Monthly Ridership data 
## (https://data.cityofchicago.org/Transportation/CTA-Ridership-L-Station-Entries-Monthly-Day-Type-A/t2rn-p8d7)

## -----------------------------------------------------------------------------
## Load Popular Libraries
## -----------------------------------------------------------------------------
library(XML)
library(xml2)

## -----------------------------------------------------------------------------
## Parse Files
## -----------------------------------------------------------------------------
doc <- XML::xmlParse("data/cta_monthly_l_rides_preview.xml")
doc2 <- xml2::read_xml("data/cta_monthly_l_rides_preview.xml")

doc

## -----------------------------------------------------------------------------
## Convenience Data Frame Methods in `XML`
## -----------------------------------------------------------------------------
cta_month_rides_df <- cbind(XML::xmlToDataFrame(nodes=getNodeSet(doc, "//row/row")),
                            XML:::xmlAttrsToDataFrame(getNodeSet(doc, "//row/row")))

cta_month_rides_df


## -----------------------------------------------------------------------------
## Alternative Data Frame Builder in `xml2`
## -----------------------------------------------------------------------------
# RETRIEVE data NODES
recs <- xml2::xml_find_all(doc2, "//row/row")

# BIND EACH CHILD TEXT AND NAME
df_list <- lapply(recs, function(r) {
  attrs <- xml2::xml_attrs(r)
  vals <- xml2::xml_children(r)
  
  data.frame(rbind(setNames(c(xml2::xml_text(vals), attrs), 
                            c(xml2::xml_name(vals), names(attrs)))),
             check.names = FALSE)
})

# COMBINE ALL DFS
cta_month_rides_df2 <- do.call(rbind.data.frame, df_list)
rm(recs, df_list)

cta_month_rides_df2


## -----------------------------------------------------------------------------
## Use of XPath (query language to search/retrieve nodes in XML documents)
## -----------------------------------------------------------------------------
doc <- XML::xmlParse("data/cta_monthly_l_rides.xml")

cta_month_rides_df <- XML::xmlToDataFrame(nodes=getNodeSet(doc, "//row/row[contains(stationame, 'Harlem-Lake') 
                                                                           and avg_weekday_rides > 4000]"))

cta_month_rides_df

## -----------------------------------------------------------------------------
## Parse More Complex Nested Structured XML
## -----------------------------------------------------------------------------
doc <- XML::xmlParse("data/cta_monthly_l_rides_nested.xml")
doc2 <- xml2::read_xml("data/cta_monthly_l_rides_nested.xml")

doc

## -----------------------------------------------------------------------------
## Use `data.frame()` Constructor to Build Data Frame 
## -----------------------------------------------------------------------------
cta_month_rides_df <- data.frame(
    t(xpathSApply(doc, "//row/station", xmlAttrs)),
    month = xpathSApply(doc, "//row/month", xmlValue),
    avg_weekday_rides = xpathSApply(doc, "//row/rides/avg_weekday_rides", xmlValue),
    avg_saturday_rides = xpathSApply(doc, "//row/rides/avg_saturday_rides", xmlValue),
    avg_sunday_holiday_rides =xpathSApply(doc, "//row/rides/avg_sunday_holiday_rides", xmlValue)
  )

cta_month_rides_df

## -----------------------------------------------------------------------------
## Use Convenience Methods with `cbind` to Build Data Frame
## -----------------------------------------------------------------------------
cta_month_rides_df <- cbind(setNames(XML:::xmlAttrsToDataFrame(getNodeSet(doc, "//row/station")), 
                                     c("staion_id", "station_name")),
                            setNames(XML::xmlToDataFrame(doc, nodes=getNodeSet(doc, "//row/month")), 
                                     "month"),
                            XML::xmlToDataFrame(doc, nodes=getNodeSet(doc, "//row/rides")))

cta_month_rides_df


## -----------------------------------------------------------------------------
## Use of XSLT (Script language to transform XML documents)
## -----------------------------------------------------------------------------

## -----------------------------------------------------------------------------
## Example below flattens nested XML to flatter version for easier import
## -----------------------------------------------------------------------------
library(xslt)

xsl_str <- '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                <xsl:output method="xml" omit-xml-declaration="yes" indent="yes"/>
                <xsl:strip-space elements="*"/>

                <xsl:template match="/response">
                 <xsl:copy>
                   <xsl:apply-templates select="row"/>
                 </xsl:copy>
                </xsl:template>
            
                <xsl:template match="row">
                 <xsl:copy>
                   <station_id><xsl:value-of select="station/@id"/></station_id>
                   <station_name><xsl:value-of select="station/@name"/></station_name>
                   <xsl:copy-of select="month|rides/*"/>
                 </xsl:copy>
                </xsl:template>        

            </xsl:stylesheet>'

style <- read_xml(xsl_str, package = "xslt")
new_xml <- xml_xslt(doc2, style)

cat(as.character(new_xml))


#################
### JSON Data
#################

## -----------------------------------------------------------------------------
## Load Popular Library
## -----------------------------------------------------------------------------
library(jsonlite)

## -----------------------------------------------------------------------------
## Read in Flat JSON
## -----------------------------------------------------------------------------
cat(paste0(readLines("data/cta_monthly_l_rides_preview.json"), collapse="\n"))

## -----------------------------------------------------------------------------
## Convenience Handler to Build Data Frame 
## -----------------------------------------------------------------------------
cta_month_rides_df <- fromJSON("data/cta_monthly_l_rides_preview.json")

cta_month_rides_df


## -----------------------------------------------------------------------------
## Read in Complex Nested JSON
## -----------------------------------------------------------------------------
cat(paste0(readLines("data/cta_monthly_l_rides_nested.json"), collapse="\n"))

raw <- fromJSON("data/cta_monthly_l_rides_nested.json")

str(raw)


## -----------------------------------------------------------------------------
## Extended `cbind` and extract, `$`, to Build Data Frame
## -----------------------------------------------------------------------------
cta_month_rides_df <- cbind(raw$station, month=raw$month, raw$rides)

cta_month_rides_df


