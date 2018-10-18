# CertMon v2.0
Certificate monitoring for SSL/TLS certificates.

This app integrates with the Qualys SSL Labs API for testing and monitoring certificates you own.  
A periodic scan will be performed every 24 hours on all servers you add to the database.  You can also generate ad-hoc scans as needed.  
*When conducting an ad-hoc scan, please be patient - this may take several minutes to return results and refresh your page.

Default user: admin<br>
Default pass: certmonpassword

For the love of all things secure, change your password.  No, there's nothing sensitive or non-public in here per-se, but please do it anyway :)

Start container/app:
`docker run -d -p 8080:8080 thatsatechnique/certmon`

Then browse to http://localhost:8080  (or wherever you are hosting it)


## Terms of Use

This is not an official SSL Labs project. Please make sure to read the official [Qualys SSL Labs Terms of Use.](https://www.ssllabs.com/downloads/Qualys_SSL_Labs_Terms_of_Use.pdf)

Also you should:
-  Only inspect/test servers and sites you own or are have explicit authority to test
-  Understand this application works by sending information to Qualys SSL Labs servers and they will have this information, however it will not be publicly posted
