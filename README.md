# PHP-FPM checkmk plugin

[![codecov](https://codecov.io/gh/elcamlost/checkmk-php-fpm-plugin/branch/main/graph/badge.svg)](https://codecov.io/gh/elcamlost/checkmk-php-fpm-plugin)

You can download php-fpm pool monitoring plugin form [CheckMK Exchange](https://exchange.checkmk.com/p/php-fpm-1).

# Upgrading from plugin version 2.0.x

Version 2.1.0 requires Checkmk 2.3.0 or later and renames the internal check plugin from `php_fpm_pools` to `php_fpm`.
The service description (`PHP-FPM Pool <name> Status`) is unchanged, so **historical graphs and performance data are preserved**.

After installing the new package, run service discovery on affected hosts — existing services will appear as vanished and new ones will be detected. Accept the changes and Checkmk will automatically reuse the existing RRD files.

# How to build mkp

```bash
bash package.sh
```

This produces `php_fpm.mkp` in the repository root.
