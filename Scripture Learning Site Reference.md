# Scripture Learning: Site Reference

How the site is put together, and how to add pages, menu links and tools. Written October 16, 2026.

## 1. How the site is built

- **Theme:** Astra, with a child theme at `/var/www/html/wp-content/themes/astra-child/`.
- **Pages use custom templates** stored in `astra-child/page-templates/`: `homepage.php`, `bible-reader.php`, `studytools.php`, `reading-order.php`, `about.php`, `prayer.php`, `coverage.php` and `verse-refs.php`.
- **There are no WordPress menus.** Appearance > Menus is greyed out. The main menu (About, Start Here, Read, Pray, Devotions, Study Tools, Verse Refs) is written directly in `homepage.php` and appears only on the homepage. Study Tools and Verse References have a logo-only banner, and the logo links back to the front page.
- **Page content** is whatever you type in the WordPress editor. Each template shows it with `the_content()` below its banner. Study Tools uses one large Custom HTML block. Verse References uses a two-line block.
- **Cloudflare** caches pages, so a saved change may not appear right away.
- **Bible text** comes from a REST route: `/wp-json/bible-study/v1/chapter?book=proverbs&chapter=4&version=KJV` (also `/books` and `/progress-all`).
- **Verse cross-reference tool:**
  - Data: 66 files in `/wp-content/uploads/crossrefs/` (for example `John.json`), built from OpenBible.info data.
  - Script: `/wp-content/uploads/crossrefs/crossref-tab.js`.
  - AI explanations: the plugin `scripture-crossref-ai` adds `/wp-json/scripture/v1/explain`. Its key lives in `wp-config.php`.

## 2. Before you change anything

1. Copy the file you are about to edit and keep a backup (for example `homepage.php.bak2`).
2. Make your change.
3. Purge the Cloudflare cache (Caching > Configuration > Purge Cache).
4. Test in a private browser window.

## 3. Add a new page

1. In `page-templates/`, copy `verse-refs.php` and rename the copy (for example `my-page.php`). This gives you the standard logo-only banner.
2. Edit the copy: the `Template Name:` comment at the top (this is the name WordPress shows), the `<title>` line, the small eyebrow line, the `<h1 class="slt-title">` heading and the `<p class="slt-intro">` text.
3. Upload it to `/wp-content/themes/astra-child/page-templates/`.
4. In WordPress, go to Pages > Add New, enter a title, and choose your template in the Template setting of the page sidebar.
5. Add the page content (a Custom HTML block or normal blocks) and publish.
6. Note the page address (for example `/my-page/`).

## 4. Add, rename or remove a link in the homepage menu

Edit `/wp-content/themes/astra-child/page-templates/homepage.php` (back it up first).

**Add a link.** Two small edits:

1. Near the top, next to the other address lines, add:

```php
$mypage_url = ($p = get_page_by_path('my-page')) ? get_permalink($p) : home_url('/my-page/');
```

The word `my-page` is the page's slug, the last part of its address.

2. Inside `<nav class="bsn-nav-links">`, add:

```php
<a href="<?php echo esc_url($mypage_url); ?>">My Page</a>
```

- **Order:** links appear in the order of the lines.
- **Rename:** change the text between the link tags.
- **Remove:** delete the link line.
- **Crowding:** seven or more links can wrap on small phone screens, so keep labels short.

## 5. Change a page's heading or title

- **Big heading on the page:** the `<h1 class="slt-title">` line in its template.
- **Browser tab text:** the `<title>` line in the template.
- **Title in the WordPress page list:** Pages > edit the page > title. Changing it does not change the page address.
- **Menu label:** the text inside the link in `homepage.php`.

## 6. Add a tab to Study Tools

- Study Tools is one large Custom HTML block. Each tab is a button plus a panel. The Novenas and Rosary tabs were added as extra code pasted at the end of that block.
- That block is big. If saving fails or changes do not show, put the code in a JavaScript file in `/wp-content/uploads/` and load it with one line at the end of the block:

```html
<script src="/wp-content/uploads/crossrefs/your-file.js?v=1"></script>
```

- Increase the `?v=` number every time you change that file so browsers fetch the new copy.

## 7. Verse References tool: settings

- **The page content** is these two lines (use the version number currently on the page):

```html
<div id="slVerseRefs"></div>
<script src="/wp-content/uploads/crossrefs/crossref-tab.js?v=3"></script>
```

- **Script settings** are in the CONFIG section at the top of `crossref-tab.js`: `DATA_BASE` (the data folder), `MAX_REFS` (how many references show, default 20) and `AUTO_EXPLAIN` (true explains every search automatically and uses more credits).
- **AI settings** are in `wp-config.php`: `define('OPENAI_API_KEY', '...');` and optionally `define('SCE_MODEL', 'model-name');`. The default model is `gpt-4.1-mini`.
- **Cost controls:** each verse's explanation is cached for 30 days, and each visitor is limited to 20 new explanations per hour. Set a monthly spending limit in your OpenAI account.
- **Update the script:** upload the new `crossref-tab.js` over the old one, then raise the `?v=` number in the page block.
- **Update the data:** upload new JSON files into the `crossrefs` folder.

## 8. Troubleshooting

- **A change does not show:** purge Cloudflare, try a private window, raise the `?v=` number, and make sure you clicked the page's own Update button, not only the block's Update.
- **The tool does not load:** press F12, open the Console tab, and look for lines starting with `[crossrefs]`.
- **Message says `HTTP 404 loading ... .json`:** that data file is missing or in the wrong folder.
- **Message says no cross-references were found:** it shows the key it looked for and the first key in the file, which reveals a format mismatch.
- **Verse text is missing:** check the reader route and the book's slug.
- **Explanations fail:** check that the plugin is active, the key is in `wp-config.php`, and the OpenAI account has credits.

## 9. Safety

- Never paste API keys into pages, blocks or JavaScript files. Keys belong only in `wp-config.php`.
- If a screenshot ever shows cookies or keys, log out everywhere (Users > Your Profile > Log Out Everywhere Else) and replace the key.
- Keep backup copies, and edit only the child theme, never the parent Astra theme.

## 10. Credits to keep on the site

- Cross-reference data: OpenBible.info, CC BY 4.0. Credit must stay visible.
- Verse text: King James Version.
