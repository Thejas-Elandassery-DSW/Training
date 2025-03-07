# Apache Configuration Guide

## 1️⃣ Reverse Proxy (Localhost)

If your backend (e.g., Flask, Node.js, Django) is running on **localhost:5000**, you can still set up Apache to proxy requests.

Edit Apache config:

```bash
sudo nano /etc/apache2/sites-available/000-default.conf
```

Modify:

```apache
<VirtualHost *:8080>
    ServerName localhost

    ProxyPreserveHost On
    ProxyPass /api http://127.0.0.1:5000/
    ProxyPassReverse /api http://127.0.0.1:5000/

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Restart Apache:

```bash
sudo systemctl restart apache2
```

Now, visiting **http://localhost:8080/api** will **forward** the request to **http://127.0.0.1:5000**.

## 2️⃣ Self-Signed SSL for Local HTTPS

Since you **don't have a domain**, you can create a **self-signed SSL certificate**.

### 🔹 Generate a Self-Signed Certificate

```bash
sudo mkdir /etc/apache2/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/ssl/apache-selfsigned.key -out /etc/apache2/ssl/apache-selfsigned.crt
```

* When asked for a **Common Name (CN)**, enter **localhost**.

### 🔹 Configure Apache for HTTPS

Edit:

```bash
sudo nano /etc/apache2/sites-available/default-ssl.conf
```

Modify:

```apache
<VirtualHost *:443>
    ServerName localhost

    SSLEngine on
    SSLCertificateFile /etc/apache2/ssl/apache-selfsigned.crt
    SSLCertificateKeyFile /etc/apache2/ssl/apache-selfsigned.key

    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

### 🔹 Enable SSL and Restart Apache

```bash
sudo a2enmod ssl
sudo a2ensite default-ssl
sudo systemctl restart apache2
```

Now, your site should be accessible at:

```
https://localhost
```

Since it's **self-signed**, your browser may show a **warning**—just **proceed anyway**.

## 3️⃣ Serve Frontend (React, Vue, Angular) Locally

Move your **frontend build** to Apache:

```bash
sudo rm -rf /var/www/html/*
sudo cp -r /path-to-frontend-build/* /var/www/html/
```

Restart Apache:

```bash
sudo systemctl restart apache2
```

Now, **http://localhost:8080** will serve your frontend.

## 4️⃣ Hide Apache Server Info (For Security)

Edit:

```bash
sudo nano /etc/apache2/conf-available/security.conf
```

Change:

```apache
ServerTokens Prod
ServerSignature Off
```

Restart Apache:

```bash
sudo systemctl restart apache2
```

Now, Apache **won't expose** its version.

## 🚀 Summary

✅ **Reverse Proxy:** Works on **http://localhost:8080/api**  
✅ **HTTPS (Self-Signed):** Works on **https://localhost**  
✅ **Frontend Hosting:** Works on **http://localhost:8080**  
✅ **Security Tweaks:** Apache version is hidden  

Let me know if you need **local DNS (custom domain like mysite.local)** or **more customizations!** 🔥
