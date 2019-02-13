chimera-t80stelops plugin
=========================


Installation
------------

On the www vm:

* Drop the html/ content in the apache html dir, i.e., /var/www/html/ ::

    cd /var/www/
    git clone https://github.com/astroufsc/chimera-t80stelops.git
    ln -s chimera-t80stelops/html/
    cd chimera-t80stelops/
    git submodule update --init --recursive

* Configure proxies for the internal www server where chimera-telops backend runs::

    # In /etc/apache2/mods-available/proxy.conf
        ProxyRequests On
        <Proxy *>
           #AddDefaultCharset off
           #Require all denied
           #Require local
           Order deny,allow
           Allow from all
        </Proxy>

    # In /etc/apache2/sites-available/000-default.conf:

    # For the t80s-telops backend:
    ProxyPass "/telops.json" "http://192.168.30.109:8080/telops"

    # For the AllSky
    ProxyPass "/images" "http://192.168.20.128:8080/images"

    # For the external camera
    ProxyPass "/extcam.jpg" "http://192.168.20.104/axis-cgi/jpg/image.cgi"

    # For the RRD graphs
    ProxyPass "/rrd" "http://192.168.30.109:8080/rrd"

    # For the Seeing monitor graph
    ProxyPass "/seeing.png" "http://ctio4lnew.ctio.noao.edu/web/CTIO/tmp/webfwhm2.jpg"

* For the LNA case::

    # For the internal camera
        ProxyPass "/intcam.jpg" "http://admin:@200.131.64.169/image.jpg"
        <Location /intcam.jpg>
        RequestHeader set Authorization "Basic YWRtaW46"
        </Location>

    # For the WebAdmin
        ProxyPass "/control" "http://127.0.0.1:5000/"

where the Basic autentication hash is given by this StackOverflow answer example: https://superuser.com/questions/704781/apache-mod-proxy-with-automatic-authentication


enable proxy module::

    a2enmod proxy
    a2enmod proxy_http
    service apache2 restart



On the internal www/telops vm:

* Install chimera::

    pip install https://github.com/astroufsc/chimera/archive/master.zip

* Install chimera-telops::

    pip install https://github.com/astroufsc/chimera-t80stelops/archive/master.zip

