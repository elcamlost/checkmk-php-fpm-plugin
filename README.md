# PHP-FPM checkmk plugin

You can download php-fpm pool monitoring plugin form [CheckMK Exchange](https://exchange.checkmk.com/p/php-fpm-1).

# Upgrading from 2.3 to 2.4

The 2.4-compatible version renames the internal check plugin from `php_fpm_pools` to `php_fpm`.
The service description (`PHP-FPM Pool <name> Status`) is unchanged, so **historical graphs and performance data are preserved**.

After installing the new package, run service discovery on affected hosts — existing services will appear as vanished and new ones will be detected. Accept the changes and Checkmk will automatically reuse the existing RRD files.

# How to build mkp

```bash
bash package.sh
```

This produces `php_fpm.mkp` in the repository root.
