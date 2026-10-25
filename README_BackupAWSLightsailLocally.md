# Copy a Lightsail WordPress Site to Local XAMPP

Goal: make an exact working copy of the live site on your own computer.

**Your server (from earlier output):** Debian on Lightsail, Apache, PHP 8.3, MariaDB 10.11, WordPress in `/var/www/html`, with `wp-config.php` one level up in `/var/www`.

**Placeholders used below** (replace with your own values):

| Placeholder | Meaning |
|---|---|
| `YOUR_LIGHTSAIL_IP` | The public IP of the instance |
| `your-key.pem` | The SSH key downloaded from your Lightsail account page |
| `DB_NAME`, `DB_USER` | Values found in `wp-config.php` (Step 2) |
| `wp_` | Table prefix, if yours differs (see `table_prefix` in `wp-config.php`) |
| `mysite` | The folder name you choose under XAMPP's `htdocs` |

---

## Part A: On the server

Connect first: `ssh -i your-key.pem admin@YOUR_LIGHTSAIL_IP`

### Step 1. Archive the files

```
cd /var/www
sudo tar -czf ~/site.tar.gz --exclude=html/phpmyadmin html wp-config.php
sudo chown admin:admin ~/site.tar.gz
```

`phpmyadmin` is only a symlink to a system folder, so it is excluded. `wp-config.php` is included on purpose because it lives outside `html`.

### Step 2. Get the database details

```
grep -E "DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|table_prefix|WP_HOME|WP_SITEURL|HTTPS|FORCE_SSL" /var/www/wp-config.php
```

Write down `DB_NAME`, `DB_USER`, `DB_PASSWORD` and `table_prefix`.

### Step 3. Export the database

```
mysqldump -u DB_USER -p --single-transaction DB_NAME > ~/db.sql
```

Enter `DB_PASSWORD` when prompted.

### Step 4. Note the live site URL

You need this for Step 10.

```
mysql -u DB_USER -p DB_NAME -e "SELECT option_name, option_value FROM wp_options WHERE option_name IN ('siteurl','home');"
```

---

## Part B: Download

### Step 5. Download both files (run on your own computer)

```
scp -i your-key.pem admin@YOUR_LIGHTSAIL_IP:~/site.tar.gz .
scp -i your-key.pem admin@YOUR_LIGHTSAIL_IP:~/db.sql .
```

WinSCP or FileZilla with the same `.pem` key also works.

### Step 6. Clean up the server

```
ssh -i your-key.pem admin@YOUR_LIGHTSAIL_IP "rm ~/site.tar.gz ~/db.sql"
```

The dump contains user data, so don't leave it on the server.

---

## Part C: On your computer (XAMPP)

### Step 7. Put the files in place

1. Extract `site.tar.gz` (7-Zip handles `.tar.gz` on Windows).
2. Copy the **contents** of the `html` folder into `C:\xampp\htdocs\mysite`.
3. Copy `wp-config.php` into that same folder, next to `wp-load.php`.

### Step 8. Create and import the database

1. Start **Apache** and **MySQL** in the XAMPP Control Panel.
2. Open `http://localhost/phpmyadmin`.
3. Create a new database (collation `utf8mb4_unicode_ci`). Using the same name as `DB_NAME` is easiest.
4. Select it, go to **Import**, and choose `db.sql`.

If the file is too large for the upload limit, use the XAMPP shell instead:

```
mysql -u root DB_NAME < db.sql
```

### Step 9. Edit `wp-config.php`

Set these values:

```php
define('DB_NAME', 'your_local_database_name');
define('DB_USER', 'root');
define('DB_PASSWORD', '');
define('DB_HOST', 'localhost');
```

Also remove or comment out, if present:

- Anything forcing HTTPS (`FORCE_SSL_ADMIN`, `$_SERVER['HTTPS'] = 'on'`)
- Hardcoded `WP_HOME` and `WP_SITEURL` lines

### Step 10. Change the site URLs

The database still points at the live address. Replace it with the local one using **either**:

**WP-CLI** (from `C:\xampp\htdocs\mysite`):

```
wp search-replace 'https://yoursite.com' 'http://localhost/mysite' --all-tables
```

**Better Search Replace plugin**, if you can log in.

Do **not** use a plain SQL find-and-replace. It corrupts serialized data.

**If you cannot log in**, temporarily add this to `wp-config.php` to get in, then run the replace:

```php
define('WP_HOME','http://localhost/mysite');
define('WP_SITEURL','http://localhost/mysite');
```

### Step 11. Open the site

- Site: `http://localhost/mysite`
- Admin: `http://localhost/mysite/wp-admin`

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Pages return 404 | Enable `mod_rewrite` in XAMPP, then go to **Settings > Permalinks** and click **Save**. If still broken, set `RewriteBase /mysite/` in `.htaccess`. |
| White screen or fatal error | Rename the folders of caching and security plugins in `wp-content/plugins` to deactivate them. |
| Plugin or PHP errors | The server runs PHP 8.3. Check XAMPP's with `php -v` and install a current XAMPP if it is older. |
| Redirects to the live site | Re-check Step 9 (hardcoded URLs) and Step 10 (search-replace). |
| Mixed or missing images | Run the search-replace again with `http://` and `https://` variants of the old URL. |
| Database connection error | Confirm MySQL is running and the database name in `wp-config.php` matches the one you created. |

## Alternative: Duplicator plugin

Installing **Duplicator** on the live site packages the files and database into one archive plus an installer. Upload both to `C:\xampp\htdocs\mysite`, open `http://localhost/mysite/installer.php`, and it handles Steps 7 to 10.
