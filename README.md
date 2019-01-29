#Installation - to start on boot automatically.
Clone repo onto rpi storage (typically /home/pi/iotSensor)

Install nginx
sudo apt-get update
sudo apt-get install nginx

Copy website to nginx sites-available and add entry to sites-enabled file.
Copy to web hosting directory
cp -r /home/pi/iotSensor/wwwroot/ /var/www/
Update default site available
open /etc/nginx/sites-available
change line:
root /var/www/html;
to:
root /var/www/wwwroot;

restart nginx
sudo systemctl restart nginx

test site loads (no data will be available yet)


#Debugging
starting the python script to collect and log data readings.. see config variables at the top of the script
python takereading2.py

starting the websever to display data in a trendy ilne chart
navigate to wwwroot dir
cd wwwroot
start simple python based webserver
python3 -m http.server 9009

navigate on browser to <rpi_ip_address>:9009 then you will see the display. 