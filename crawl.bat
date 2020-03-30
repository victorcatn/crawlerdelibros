@echo off
if "%1" == "" (
	echo agrege el numero maximo de paginas despues del comando, por ejemplo para dos paginas es: crawl.bat 2
	exit)

echo realizando el scraping, espere un momento

python -m scrapy crawl crawlerPlaneta -a maxpag=%1
python -m scrapy crawl crawlerPana -a maxpag=%1