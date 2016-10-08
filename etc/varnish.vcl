# This a configuration file for varnish.
# It was generated by plone.recipe.varnish.
# See the vcl(7) man page for details on VCL syntax and semantics.
#
vcl 4.0;

import std;

# configure all backends
backend backend_000 {
   .host = "127.0.0.1";
   .port = "5001";
   .connect_timeout = 0.4s;
   .first_byte_timeout = 300s;
   .between_bytes_timeout  = 60s;
}


sub vcl_init {

}

acl purge {
    "localhost";
    "127.0.0.1";
}

sub vcl_recv {
    set req.backend_hint = backend_000;
    set req.http.grace = "none";

    if (req.method == "PURGE") {
        # Not from an allowed IP? Then die with an error.
        if (!client.ip ~ purge) {
            return (synth(405, "This IP is not allowed to send PURGE requests."));
        }
        return(purge);
    }

    if (req.method == "BAN") {
            # Same ACL check as above:
            if (!client.ip ~ purge) {
            return(synth(403, "Not allowed."));
            }
            #ban("req.url ~ " + req.url);
        ban("req.http.host == " + req.http.host +
            " && req.url == " + req.url);
            # Throw a synthetic page so the
            # request won't go to the backend.
            return(synth(200, "Ban added"));
    }

    if (req.method == "USERINFO" ||
        req.method == "CONNECT" ||
        req.method == "QUIT") {
        return (synth(501, "Not implemented"));
    }

    # Only deal with "normal" types
    if (req.method != "GET" &&
           req.method != "HEAD" &&
           req.method != "PUT" &&
           req.method != "TRACE" &&
           req.method != "OPTIONS" &&
           req.method != "DELETE") {
        /* Non-RFC2616 or CONNECT which is weird. */
        return(pipe);
    }

    # Only cache GET or HEAD requests. This makes sure the POST requests are always passed.
    if (req.method != "GET" && req.method != "HEAD") {
        return(pass);
    }

    if (req.http.Expect) {
        return(pipe);
    }

    if (req.http.If-None-Match && !req.http.If-Modified-Since) {
        return(pass);
    }

    /* Do not cache other authorized content by default */
    if (req.http.Authenticate || req.http.Authorization) {
        return(pass);
    }

    if (req.url ~ "@@registration|@@login|@@resetpassword") {
        return(pass);
    }

    if (req.url ~ "^[^?]*\.(svg|css|js|png|gif|jpeg|jpg|ttf|woff|woff2)(\?.*)?$") {
       unset req.http.Cookie;
    }

    if (req.http.Cookie && req.http.Cookie ~ "auth_tkt") {
        return(pass);
    }

    unset req.http.Accept-Encoding;

    return(hash);
}

sub vcl_pipe {
    # By default Connection: close is set on all piped requests, to stop
    # connection reuse from sending future requests directly to the
    # (potentially) wrong backend. If you do want this to happen, you can undo
    # it here.
    # unset bereq.http.connection;

    return(pipe);
}

sub vcl_pass {
    return (fetch);
}

sub vcl_hash {
    hash_data(req.url);
    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }
    if (req.http.X-Forwarded-Proto) {
        hash_data(req.http.X-Forwarded-Proto);
    }
    return (lookup);
}

sub vcl_purge {
    return (synth(200, "Purged"));
}

sub vcl_hit {
    if (obj.ttl >= 0s) {
        // A pure unadultered hit, deliver it
        # normal hit
        return (deliver);
    }

    // Object is in grace, deliver it
    // Automatically triggers a background fetch
    if (obj.ttl + obj.grace > 0s) {
        set req.http.grace = "normal(limited)";
        return (deliver);
    }

    if (req.method == "PURGE") {
        set req.method = "GET";
        set req.http.X-purger = "Purged";
        return(synth(200, "Purged. in hit " + req.url));
    }

    // fetch & deliver once we get the result
    return (fetch);
}

sub vcl_miss {
    if (req.method == "PURGE") {
        set req.method = "GET";
        set req.http.X-purger = "Purged-possibly";
        return(synth(200, "Purged. in miss " + req.url));
    }

    // fetch & deliver once we get the result
    return (fetch);
}

sub vcl_backend_fetch{
    return (fetch);
}

sub vcl_backend_response {
    # The object is not cacheable
    if (beresp.http.Set-Cookie) {
        set beresp.http.X-Cacheable = "NO - Set Cookie";
        set beresp.ttl = 0s;
        set beresp.uncacheable = true;
    } elsif (beresp.http.Cache-Control ~ "private") {
        set beresp.http.X-Cacheable = "NO - Cache-Control=private";
        set beresp.uncacheable = true;
        set beresp.ttl = 120s;
    } elsif (beresp.http.Surrogate-control ~ "no-store") {
        set beresp.http.X-Cacheable = "NO - Surrogate-control=no-store";
        set beresp.uncacheable = true;
        set beresp.ttl = 120s;
    } elsif (!beresp.http.Surrogate-Control && beresp.http.Cache-Control ~ "no-cache|no-store") {
        set beresp.http.X-Cacheable = "NO - Cache-Control=no-cache|no-store";
        set beresp.uncacheable = true;
        set beresp.ttl = 120s;
    } elsif (beresp.http.Vary == "*") {
        set beresp.http.X-Cacheable = "NO - Vary=*";
        set beresp.uncacheable = true;
        set beresp.ttl = 120s;


    # ttl handling
    } elsif (beresp.ttl < 0s) {
        set beresp.http.X-Cacheable = "NO - TTL < 0";
        set beresp.uncacheable = true;
    } elsif (beresp.ttl == 0s) {
        if (bereq.http.Cookie && bereq.http.Cookie ~ "auth_tkt") {
            set beresp.http.X-Cacheable = "NO - TTL = 0";
            set beresp.uncacheable = true;
        } else {
            set beresp.http.X-Cacheable = "YES, 3600s";
            set beresp.ttl = 3600s;
            set beresp.grace = 36000s;
        }

    # Varnish determined the object was cacheable
    } else {
        set beresp.http.X-Cacheable = "YES";
    }

# https://www.varnish-cache.org/trac/wiki/VCLExampleLongerCaching
    if (beresp.ttl == 31536000s) {  # for deform.js, jquery.form-3.09.js from deformstatic
        /* Remove Expires from backend, it's too long */
        unset beresp.http.expires;

        /* Set the clients TTL on this object */
        set beresp.http.cache-control = "max-age=86400";

        /* Set how long Varnish will keep it */
        set beresp.ttl = 86400s;
    }

    # Do not cache 5xx errors
    if (beresp.status >= 500 && beresp.status < 600) {
        unset beresp.http.Cache-Control;
        set beresp.http.X-Cache = "NOCACHE";
        set beresp.http.Cache-Control = "no-cache, max-age=0, must-revalidate";
        set beresp.ttl = 0s;
        set beresp.http.Pragma = "no-cache";
        set beresp.uncacheable = true;
        return(deliver);
    }

    return (deliver);
}

sub vcl_deliver {
    set resp.http.grace = req.http.grace;
    if (obj.hits > 0) {
         set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }
    /* Rewrite s-maxage to exclude from intermediary proxies
      (to cache *everywhere*, just use 'max-age' token in the response to avoid
      this override) */
    if (resp.http.Cache-Control ~ "s-maxage") {
        set resp.http.Cache-Control = regsub(resp.http.Cache-Control, "s-maxage=[0-9]+", "s-maxage=0");
    }
    /* Remove proxy-revalidate for intermediary proxies */
    if (resp.http.Cache-Control ~ ", proxy-revalidate") {
        set resp.http.Cache-Control = regsub(resp.http.Cache-Control, ", proxy-revalidate", "");
    }

    unset resp.http.Server;

}

/*
 We can come here "invisibly" with the following errors: 413, 417 & 503
*/
sub vcl_synth {
    set resp.http.Content-Type = "text/html; charset=utf-8";
    set resp.http.Retry-After = "5";

    synthetic( {"
        <?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html>
          <head>
            <title>Varnish cache server: "} + resp.status + " " + resp.reason + {" </title>
          </head>
          <body>
            <h1>Error "} + resp.status + " " + resp.reason + {"</h1>
            <p>"} + resp.reason + {"</p>
            <h3>Guru Meditation:</h3>
            <p>XID: "} + req.xid + {"</p>
            <hr>
            <p>Varnish cache server</p>
          </body>
        </html>
    "} );

    return (deliver);
}
