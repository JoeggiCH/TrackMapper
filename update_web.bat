@echo off
REM this is an example of a batch to publish html\map.html on a webpage
REM please adjust it to your needs!

date /t
time /t
cd %1
copy html\map.html joeggiCH.github.io
cd  joeggiCH.github.io
@echo on
git pull --rebase
git add map.html
git commit -m "map update"
git push
