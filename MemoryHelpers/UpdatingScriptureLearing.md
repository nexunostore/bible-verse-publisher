# Scripture Learning: WordPress Site Guide for Developers

*Prepared 27 November 2026 from an export of the site's custom code and WP-CLI output, plus changes made afterwards (Prayer Library page, shared responsive menu). It contains no passwords or API keys. Items marked **To confirm** could not be verified from the export.*

---

## 1. Overview

Scripture Learning is a Bible study site built on WordPress. The public site has:

- a Bible reader (KJV/ASV text with notes, highlights and reading progress)
- a daily prayer and daily verse
- study tools (maps, charts, family trees)
- a cross-reference explorer
- an AI-drafted Bible Questions section
- a searchable Prayer Library
- a private reading tracker
- a blog-style Devotions section of study notes that are generated and published automatically

Almost everything custom lives in these places:

- **The child theme** `astra-child`: page templates, the shared menu, styles, the Prayers post type.
- **Six custom plugins**: the Bible database and REST API, audio generation, AI tools, the reading tracker and the novenas tool.
- **Two upload folders** holding standalone scripts: `wp-content/uploads/prayer-library/` and `wp-content/uploads/crossrefs/`.

The theme does **not** use Astra's header or footer on custom pages. Each page template is a complete, standalone HTML document. The site menu is printed by one shared function, `bsn_render_nav()` (section 4).

---

## 2. Hosting and versions

- **Host:** AWS Lightsail instance running the Lightsail-packaged WordPress blueprint (not Bitnami).
- **WordPress:** 7.1.5. **PHP:** 8.3.
- **WordPress folder:** `/var/www/html`. `wp-config.php` sits one level above, in `/var/www`.
- **Server user:** `admin` (SSH). Files served by the web server are owned by `www-data`.
- **Web server:** not confirmed from the export (To confirm: `apachectl -v`).
- **Parent theme:** Astra 4.13.11 (an update to 4.14.3 was available). **Child theme:** `astra-child` 1.0.0, active.
- **CDN/cache:** code comments refer to Cloudflare caching the reader page (To confirm the Cloudflare setup, DNS and SSL). WP Super Cache is installed but inactive.
- **WP-CLI** is installed. Run commands from `/var/www/html` with `--allow-root`.
- **Comments** are disabled site-wide in the child theme's `functions.php`.

**Before changing anything, take a Lightsail snapshot** (instance page, Snapshots tab).

---

## 3. Plugins

**Custom (written for this site):**

| Plugin | Location | What it does |
|---|---|---|
| Bible Reader (`bible-study-notes` v1.1.0) | `plugins/bible-study-notes/` | Database tables, REST API, notes, highlights, progress, GitHub trigger |
| BSN Post Audio (v1.5) | `plugins/bsn-post-audio.php` | Generates an MP3 for each post |
| Scripture Cross-Reference Explainer (v1.0) | `plugins/scripture-crossref-ai.php` | REST endpoint that explains cross-references with OpenAI |
| Scripture Questions (v1.0) | `plugins/scripture-questions/` | Admin tool that drafts Bible Question pages with OpenAI |
| Scripture Reading Tracker (v1.1.0) | `plugins/scripture-reading-tracker/` | Private per-user reading tracker |
| Scripture Novenas (v1.0.0) | `plugins/scripture-novenas/` | `[scripture_novenas]` shortcode with eight public-domain novenas |

**Third-party, active:** Code Snippets (no snippets have been created), WP Mail SMTP, WPS Hide Login (the login page is not at `/wp-login.php`; the custom address is kept private and is not recorded here), WP Statistics.

**Third-party, inactive:** Query Monitor, WP Super Cache.

**Custom post types:** `bsn_prayer` (Prayers, from the theme) and `sl_question` (Bible Questions, from the Scripture Questions plugin).

---

## 4. The child theme (`astra-child`)

Folder: `wp-content/themes/astra-child/`

### functions.php

- `bsn_logo_icon()` outputs the open-book SVG logo used in the menu.
- `bsn_page_url_by_template($template_file)` finds the permalink of whichever page uses a given template. **Renaming or moving a template file breaks the links that depend on it.**
- **`bsn_render_nav($style)` prints the site menu.** `$style` is `'dark'` (white links, for pages with a dark banner) or `'light'` (dark links, for pale pages). See "The shared menu" below.
- Loads the Astra parent stylesheet.
- On every front-end page: enqueues `assets/nav.css` and `assets/nav.js` (menu styles and behaviour). The version number `2.0` in these enqueue calls is the cache-buster; raise it when you change either file.
- On the Bible Reader template only: enqueues Google Fonts, `assets/reader.css`, `assets/reader.js` and Alpine.js (loaded after reader.js on purpose; do not reorder). It passes `BibleReaderConfig` (REST base URL and nonce) to the script.
- On the Homepage, Prayer, Reading Order and About templates, and on the blog index, single posts and archives: enqueues `assets/homepage.css`. **A new template that needs the site's standard page styling must be added to this condition.**
- Registers the `bsn_prayer` post type and seeds five starter prayers once.
- Disables comments everywhere and removes comment menus.

### The shared menu

The menu is: About, **Start Here** (dropdown: Study Tools, Verse References, Bible Questions), Read, **Pray** (dropdown: Prayer Library), Devotions.

- **To change the menu, edit `bsn_render_nav()` in `functions.php`.** There is one copy, and every page that uses it updates at once.
- **Markup:** `header.bsn-nav` containing the logo, a menu button `.bsn-burger` and `nav.bsn-nav-links`. A dropdown is a `div.bsn-sub` holding the main link, a toggle button `.bsn-sub-toggle` and a `div.bsn-sub-menu` of sub-links.
- **Desktop and landscape tablet (wider than 760px):** a horizontal menu. Dropdowns open on mouse hover, or when the ▾ arrow is tapped on a touch screen.
- **Phone and portrait tablet (760px and narrower):** the logo text is hidden and the three-line button opens a vertical panel, with the sub-pages indented under their parent.
- **Styles:** `assets/nav.css`. **Behaviour:** `assets/nav.js` (toggles the `is-open` class and `aria-expanded`). Both are self-contained and loaded on every front-end page by `functions.php`.
- `'dark'` and `'light'` only change colours: `light` adds the class `bsn-nav--light` for pale pages.
- The old dropdown script `/wp-content/uploads/crossrefs/nav-dropdown.js` and the `bsn-dd` classes are no longer used. The file can be deleted once the site has been checked, and any leftover `.bsn-dd` rules in the Customizer's Additional CSS can be removed.
- The home page banner is pulled up under the menu with a negative top margin (`margin-top:-88px` on `.bsn-hero` in `homepage.css`). If the menu's height changes, check the home page for a gap above the banner.
- Backups from when the shared menu was introduced, on the server and outside the web folder: the original ten templates are in `/home/admin/nav-backup/`, and the earlier `functions.php` is `/home/admin/functions.php.before-menu-fix`.

**Templates that call `bsn_render_nav()`:** `home.php`, `single.php`, `archive.php`, `homepage.php`, `reading-order.php`, `studytools.php`, `verse-refs.php`, `prayer-library.php` (all `'dark'`), and `prayer.php`, `about.php` (`'light'`).

**Pages that do not use it:** the Bible Reader (its own app-style top bar), the private coverage page, pages on the default Astra template (they show Astra's header), and the Bible Questions pages, which come from the plugin's own templates (`plugins/scripture-questions/templates/common.php` has a logo-only header; it can be switched to `<?php if (function_exists('bsn_render_nav')) bsn_render_nav('dark'); ?>` if wanted).

### Templates in the theme root

- `home.php`: the Posts page (Devotions), with its own search and category filtering (`?s=`, `?study_cat=`).
- `single.php`: individual study posts.
- `archive.php`: date, category, tag and author archives.

### Page templates (`page-templates/`)

- `homepage.php`: home page; daily verse and the explorer block.
- `bible-reader.php`: the Bible reader (Alpine.js app).
- `prayer.php`: today's prayer.
- `reading-order.php`: curated reading path (hardcoded list in the file).
- `about.php`: About page (hardcoded text).
- `studytools.php`: Study Tools hero plus the page's own Custom HTML block.
- `verse-refs.php`: Verse References hero plus a Custom HTML block that loads a script.
- `prayer-library.php`: Prayer Library page (copy of `verse-refs.php` with its own heading).
- `coverage.php`: private Post Coverage page (admin only).
- `hompageNAVUpdate.php`: an older copy of the homepage template (see section 8).

### Assets

`assets/reader.js`, `reader.css`, `homepage.css`, `nav.css`, `nav.js`, plus backup copies (see section 8).

---

## 5. Custom plugins and tools in detail

### Bible Reader (`bible-study-notes`)

**Database tables** (created on activation and kept in sync by a version check on every load):

- `{prefix}study_notes`: one note per book, chapter and verse range.
- `{prefix}verse_highlights`: highlights per visitor.
- `{prefix}chapter_progress`: chapters read per visitor.
- `{prefix}bible_verses` and `{prefix}bible_books`: the KJV/ASV text and book list. These are built by a separate import script, `import-bible.php`, which was not in the export (To confirm where it lives).

**Visitor identity:** logged-in users are `u{ID}`; everyone else gets an anonymous cookie, `bsn_visitor_id`, created only when someone first highlights or records progress. This keeps the reader page cookie-free so Cloudflare can cache it. **Do not set cookies on page load.**

**REST API**, base `/wp-json/bible-study/v1/`:

- `GET /notes?book=&chapter=`: notes for a chapter (public).
- `POST /notes`: create or replace a note (administrator only).
- `GET /books`, `GET /chapter`: Bible structure and text used by the reader.
- `GET/POST /highlights`, `GET/POST /progress`, `GET /last-read`, `GET /progress-all`: per-visitor features.
- `POST /trigger-note`: starts a GitHub Actions workflow that generates a study note (administrator only).
- `GET/POST /coverage`: which chapters already have a published post, kept in the option `bsn_chapter_coverage` (administrator only).

**Automation:** a GitHub Actions workflow publishes notes and posts back into WordPress through the REST API using an Application Password (Users > Profile > Application Passwords). The workflow files were not in the export (To confirm: repository name and workflow file names).

### BSN Post Audio

When a post is saved (published, draft or pending), it schedules a background WP-Cron job about 30 seconds later. The job sends the text to OpenAI text-to-speech (model `tts-1`, voice `onyx`, speed 0.85) and saves an MP3 named after the post slug. The audio URL is stored in post meta `_bsn_audio_url` and any error in `_bsn_audio_error`. Audio is generated once per post, so republishing does not trigger a second paid call. An admin menu page shows queue status and errors. If audio fails to save, check that the uploads folder is owned by `www-data`.

### Scripture Cross-Reference Explainer

Public endpoint `POST /wp-json/scripture/v1/explain`. It validates input (verse, text, up to 25 references), checks a cache (30 days), and applies a rate limit of 20 uncached requests per IP per hour before calling OpenAI. It is used by the Verse References page through `crossref-tab.js`.

### Scripture Questions

Adds the **Bible Questions** menu (post type `sl_question`, archive at `/questions/`, topic taxonomy at `/question-topic/`). The submenu **Ask a Question** takes a question and drafts a study page with exact KJV quotes pulled from the site's own database (AJAX action `sq_generate`). It uses its own templates in the plugin's `templates/` folder through the `template_include` filter.

### Scripture Reading Tracker

Shortcode `[bible_tracker]`. Progress is stored per logged-in user in user meta `bibletracker_progress`, through the REST route `/wp-json/bibletracker/v1/progress`. The page holding the shortcode is set to Private.

### Scripture Novenas

Shortcode `[scripture_novenas]` renders a self-contained app (its CSS and JS are printed in the footer only when the shortcode is on the page). No published page in the page export currently uses it (To confirm).

### Prayer Library (a page tool, not a plugin)

A browser-only app that lists prayer books with search, categories, favorites and a link to the full PDF. It has no database tables and no REST routes. Its files live in `wp-content/uploads/prayer-library/`, outside the theme and plugins, so theme updates do not touch them:

- `prayer-library.js`: draws the interface into `<div id="slPrayerLib"></div>`. Options on that div: `data-books` (comma-separated book ids, default `prayers`), `data-v` (data version), `data-theme` (light, dark or auto), `data-base` (folder path).
- `data/prayers.js`: the book's details and its entries (title, PDF page number, category, text).
- `covers/prayers.jpg` and `books/prayers.pdf`: the cover and the full prayer book.

The page (slug `prayer-library`) uses the `prayer-library.php` template and one Custom HTML block:

```html
<!-- wp:html -->
<style>
body #slPrayerLib{max-width:none !important;margin:0 24px 30px !important}
</style>
<div id="slPrayerLib"></div>
<script src="/wp-content/uploads/prayer-library/prayer-library.js?v=1"></script>
<!-- /wp:html -->
```

The style line makes the library full width; remove it to return to the default centred 820px layout. The block editor's visual view can hide a Custom HTML block, so use the **Code editor** (three dots, top right) to see everything. **Never add a second copy:** running the script twice shows every book twice.

**To add another book:** put `<id>.js` in `data/`, `<id>.jpg` in `covers/` and `<id>.pdf` in `books/`, add the id to `data-books` on the container div, and raise the `?v=` number on the script tag and the `data-v` value so browsers fetch the new files.

---

## 6. How each existing page works

| Page | ID | Template | Notes |
|---|---|---|---|
| Home | 12 | `homepage.php` | Daily verse (cached in a transient `bsn_votd_YYYY-MM-DD`) plus a Custom HTML explorer block, styled by `homepage.css` |
| Reader | 9 | `bible-reader.php` | The Alpine.js reader. No editable content |
| Pray | 14 | `prayer.php` | One prayer a day from the Prayers post type. Add prayers in wp-admin > Prayers |
| Devotions | 16 | default | Appears to be the Posts page, rendered by `home.php` (To confirm in Settings > Reading) |
| Study Tools | 191 | `studytools.php` | Hero in the template, content in the page's Custom HTML block |
| Reading Order | 71 | `reading-order.php` | The book list is a PHP array in the template. Edit the file to change it |
| Verse References | 781 | `verse-refs.php` | Custom HTML block loads `/wp-content/uploads/crossrefs/crossref-tab.js` (not in the export; To confirm) |
| About | 101 | `about.php` | Text is hardcoded in the template |
| Bible Reading Tracker | 203 (private) | `coverage.php` | Contains `[bible_tracker]` but uses the coverage template (To confirm this is intended) |
| Prayer Library | new | `prayer-library.php` | Custom HTML block loads the library (section 5) |
| Privacy Policy | 3 (draft) | default | Still the WordPress default text |

---

## 7. How to add a new page

**Option A: a normal content page.** Pages > Add New, write the content, publish. This uses Astra's default layout, so it shows Astra's header rather than the site menu. Fine for utility pages; it will look different from the rest of the site.

**Option B: a page that matches the site (recommended).**

1. **Snapshot first** (section 2).
2. **Copy a template** in `wp-content/themes/astra-child/page-templates/`:
   - Hero banner with editable content below: copy `verse-refs.php` (this is how the Prayer Library page was made). It carries its own inline CSS.
   - Simple text page on a pale background: copy `about.php`.
3. **Edit the copy:** change the `Template Name:` line at the top (this is the name shown in the page editor), the `<title>`, the heading text and the `body_class`. Leave the `bsn_render_nav('dark')` or `bsn_render_nav('light')` line in place, so the menu appears automatically.
4. **If the copy relies on `homepage.css`** (like `about.php`), add the new template to the condition in the `homepage.css` block of `functions.php`. If you skip this, the page appears unstyled. The menu itself is styled everywhere by `nav.css`.
5. **Create the page:** Pages > Add New, set Template to your new template in Page Attributes, add content, publish.
6. **Add it to the menu (optional):** edit `bsn_render_nav()` in `functions.php`, once. Build the URL the same way as the others, for example `get_page_by_path('my-slug')`, and add an `<a>` to the list, or inside an existing `bsn-sub-menu` to put it in a dropdown. Then test the menu on a phone as well as a desktop.
7. **Check the page** logged out and on mobile, after clearing any Cloudflare cache.

**A page that needs data or interactivity:** add a REST route or shortcode in a plugin (not the theme), and load scripts only on that template, following the pattern used for the reader in `functions.php`.

---

## 8. Gotchas and cleanup

- **Backup files in public folders.** The theme and plugin folders contain backup copies (for example `.bak` files for the main plugin, `reader.BFMoveNotePlane.js.bk`, `hompage_backup.css`, `archive_backup.php`, `common_backup.php`, a hidden `.reader.js`, and a `scripture-questions.zip` in the plugins folder). Move them out of the web root. Never edit one thinking it is live. The live files are the ones named in this guide.
- **Two templates named "Homepage".** `homepage.php` and `hompageNAVUpdate.php` both declare `Template Name: Homepage`. The Home page uses `homepage.php`. Rename or remove the other to avoid picking the wrong one.
- **Duplicate block on Verse References.** The page content contains the same `slVerseRefs` block twice (one loading `crossref-tab.js?v=2`, one `?v=4`). Remove the old one.
- **Privacy Policy** still contains the default text with `http://127.0.0.1` in it. Replace it before publishing.
- **Hidden Custom HTML blocks.** On pages built from a template plus one Custom HTML block (Study Tools, Verse References, Prayer Library), the block can be invisible in the visual editor. Open the Code editor before adding another, or the content will be duplicated.
- **Browser caching of scripts and data.** After changing `prayer-library.js`, its data files, `crossref-tab.js`, `nav.css` or `nav.js`, raise the version number where the file is loaded (the `?v=` on a script tag, or the `'2.0'` in the enqueue calls in `functions.php` for the menu), or visitors keep seeing the old version.
- **Test the menu on a phone and a tablet after any change.** It has two layouts, and a problem often shows on only one.
- **Secrets live outside the code.** API keys and GitHub credentials are defined in `wp-config.php`, not in plugin files. Keep it that way. Never commit or share `wp-config.php`.
- **Template renames break links** because URLs are resolved from template file names.
- **Cloudflare caching:** pages must not send cookies on load or they will stop being cached.
- **Updates:** update Astra on a snapshot copy first, since the child theme depends on it. Several plugins have auto-update turned off on purpose, and the custom ones have no update source.
- **Bible text tables** are not rebuilt by WordPress. If the database is restored without them, the reader and the home page verse break.

---

## 9. Configuration reference (names only, no values)

Defined in `wp-config.php`:

- `OPENAI_API_KEY`: cross-reference explainer and Scripture Questions.
- `BSN_OPENAI_API_KEY` (or the environment variable `OPENAI_API_KEY`): post audio.
- `SCE_MODEL`, `SQ_MODEL`, `SQ_STYLE_NOTES`: optional model and style settings.
- `BSN_GITHUB_TOKEN`, `BSN_GITHUB_OWNER`, `BSN_GITHUB_REPO`, `BSN_GITHUB_WORKFLOW_FILE`: used by `/trigger-note`.

Stored in the database: options `bsn_db_version`, `bsn_prayers_seeded`, `bsn_chapter_coverage`; user meta `bibletracker_progress`; post meta `_bsn_audio_url` and `_bsn_audio_error`; transients for the daily verse, cross-reference cache and rate limits.

---

## 10. How to update the site

All custom code lives in the child theme, the six custom plugins, and the two upload folders. Everything else is stock WordPress and can be updated the normal way.

### Before any change

1. Take a Lightsail snapshot.
2. Copy any file you are about to edit to your home folder, not the web folder: `cp file.php ~/file.php.orig`. Do not leave `.bak` files inside the web root.
3. Edit over SSH with `sudo nano <file>` or over SFTP. Keep the owner and permissions the same: `sudo chown --reference=<other file in the folder> <new file>`.
4. For PHP files, run `php -l <file>` first. It reports a syntax error before it can take the site down.
5. When scripting edits with `sudo python3`, use full paths such as `/home/admin/...`. Under `sudo`, `~` means `/root`.

### Where to change what

- **A new page:** section 7.
- **The menu:** `bsn_render_nav()` in `functions.php`.
- **Daily prayers:** wp-admin > Prayers.
- **Study posts and notes:** created automatically through GitHub and the REST API; fix individual posts in wp-admin > Posts.
- **Bible Questions:** wp-admin > Bible Questions > Ask a Question.
- **Prayer Library content:** `uploads/prayer-library/data/<book>.js` (section 5).
- **Reading Order list and About text:** the PHP file of that template.
- **Styles:** `assets/nav.css` and `assets/nav.js` (menu), `assets/homepage.css`, `assets/reader.css`, and the inline CSS inside `studytools.php` and `verse-refs.php`.
- **Plugin behaviour:** the plugin's own folder under `wp-content/plugins/`.

### Updating WordPress, plugins and Astra

Run from `/var/www/html`, after a snapshot:

```bash
wp core update --allow-root
wp plugin update wp-mail-smtp wp-statistics wps-hide-login code-snippets --allow-root
wp theme update astra --allow-root
```

The custom plugins have no update source, so **never run `wp plugin update --all`**. Astra is the parent of the child theme, so test the front page, Reader and a post right after updating it.

### After a change

- Hard refresh in the browser, and clear the Cloudflare cache if it is in use.
- Raise the `?v=` number on any script or data file you changed.
- Check logged out: Home (dropdown menus open, and the menu button works on a phone), Reader (a chapter loads), Pray, Prayer Library, Verse References, a Devotions post and a Bible Question.
- Confirm the hidden login address still works.

### Useful commands

```bash
cd /var/www/html
wp core version --allow-root
wp plugin list --fields=name,status,version,file --allow-root
wp theme list --allow-root
wp post-type list --allow-root
wp post list --post_type=page --fields=ID,post_title,post_name,post_status --allow-root
php -v
```

### Backing up and rolling back

- **Whole server:** a Lightsail snapshot. Restore by creating a new instance from the snapshot, then moving the static IP to it.
- **One file:** copy back the `.orig` copy from your home folder.
- **Database:** `wp db export ~/site-$(date +%F).sql --allow-root`, then download it and keep it off the server. It contains visitor and account data, so store it privately.
- Snapshot schedule: To confirm.

---

## 11. Handoff checklist for a new developer

**Access the owner needs to arrange (never write these in this document):**

- A named WordPress administrator account for the developer, not a shared login.
- SSH or Lightsail console access to the instance.
- The GitHub repository that generates and publishes study notes.
- Cloudflare and the domain's DNS, if used.
- The OpenAI account behind the keys in `wp-config.php`, and the SMTP provider behind WP Mail SMTP.

**First day:**

1. Read sections 1 to 5, then open `functions.php`, `homepage.php` and `bible-study-notes.php`.
2. Run the commands in "Useful commands" to confirm this guide matches the live site.
3. Add a test page using section 7 on a snapshot copy, not the live site.

**Cleanup worth doing first:**

1. Move the backup and zip files out of the web folders (section 8).
2. Remove the duplicate `Homepage` template and the duplicate block on Verse References.
3. Replace the Privacy Policy text and publish it.
4. Decide whether the tracker page should use the `coverage.php` template.
5. Fill in every "To confirm" item in this guide and in the list below.

---

## 12. Items to fill in

These were not available in the export. Add them before handing this guide over:

- Location and contents of `import-bible.php` and `crossref-tab.js`.
- GitHub repository and workflow file names for note and post generation.
- DNS provider, Cloudflare settings, SSL method and Lightsail static IP.
- Backup and snapshot schedule.
- Where the credentials are kept and who has access (do not write them in this document).
