# iislp
<b>IIS</b> Web <b>l</b>og <b>P</b>arser

This will read in IIS Web logs and parse out certain types of logs and the info they contain.  That all gets saved into a CSV file. 

This was a side project that was eventually scrapped in favor of using Splunk to parse web logs. The whole process was as follows: 

-Every morning the new web logs would be parsed and all the relavant log information was saved into the CSV files.  
-The CSV files were ftp'd to a Debian VM I set up to run on the server  
-Once the CSV files arrived, a Java application watching that directory would take the CSV and upload it to a Neo4j graph database  
-From there queries could be made  

This project was a learning experience for Python and Neo4j, both of which I like very much.
