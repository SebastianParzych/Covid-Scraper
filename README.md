# Covid-19 data Scraper
###
## Scraper
Scraper is providing valuable data about covid from https://www.worldometers.info/coronavirus/.
There is an option to chosoe from which country we want to obtain or update a data. All of them are converted to dataFrame and then to  .csv file. This file is saved in a data folder.
### Working principle
Covid-19 data in single country is stored in charts. The number of charts and type of data they contain varies by country.
Entire data is saved directrly in scripts, in which they are occured  in json format. The main goal was to obtain the data in way ,that one algorithm 
could fit to each country, that's why  I chose algotithm that includes operations on strings. In general scraper  splits script depending on how many 
times phrase 'data:' is occurred, while checking whether the data is repeated ( Linear and log scales of charts have same values of data, but they 
make seperate datasets in script). Labels of datasets are extracted  in the same way.</br>
Example of exctraction one dataset.
   ```PY
   last_str = last_str.split('data:', 1)[1]
   last_str = last_str.split(']', 1)[0].replace('[', '').replace(' ', '')
   ```
###
