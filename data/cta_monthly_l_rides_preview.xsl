<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" omit-xml-declaration="yes" indent="yes"/>
    <xsl:strip-space elements="*"/>
    
    <xsl:template match="/response/row">
     <response>
       <xsl:apply-templates select="row"/>
     </response>
    </xsl:template>
    
    <xsl:template match="row">
     <xsl:copy>
        <station>
          <xsl:attribute name="id"><xsl:value-of select="station_id"/></xsl:attribute>
          <xsl:attribute name="name"><xsl:value-of select="stationame"/></xsl:attribute>
        </station>
        <month><xsl:value-of select="month_beginning"/></month>
        <rides>
          <xsl:copy-of select="avg_weekday_rides|avg_saturday_rides|
                                avg_sunday_holiday_rides|month_total"/>
        </rides>
     </xsl:copy>
    </xsl:template>
    
    <!-- <xsl:template match="row[count(preceding-sibling::row) &gt; 4 and      -->
    <!--                          count(preceding-sibling::row) &lt; 33755]"/>  -->
                             
</xsl:stylesheet>
