admins = { }
daemonize = false
modules_enabled = {
    "roster";
    "saslauth";
    "tls";
    "dialback";
    "disco";
    "posix";
    "register";  -- Allow account registration
}

modules_disabled = { }

allow_registration = true
c2s_require_encryption = false
s2s_require_encryption = false
authentication = "internal_plain"

-- Logging configuration
log = {
    info = "*console";
    error = "*console";
}

pidfile = "/var/run/prosody/prosody.pid"

VirtualHost "prosody"
    enabled = true
    ssl = {
        key = "/etc/prosody/certs/prosody.key";
        certificate = "/etc/prosody/certs/prosody.crt";
    }
