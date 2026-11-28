Scripture Learning – WordPress Site Guide for Developers
Prepared 27 November 2026 from an export of the site's custom code and WP-CLI output. It contains no passwords or API keys. Items marked To confirm could not be verified from the export.
1. Overview
Scripture Learning (scripturelearning.org) is a Bible study site built on WordPress. The public site has a Bible reader (KJV/ASV text with notes, highlights and reading progress), daily prayer and verse, study tools (maps, charts, family trees), a cross-reference explorer, an AI-drafted Bible Questions section, a private reading tracker, and a blog-style Devotions section of study notes that are generated and published automatically.
Almost everything custom lives in two places:
• The child theme astra-child: page templates, navigation, styles, the Prayers post type.
• Six custom plugins: the Bible database and REST API, audio generation, AI tools, the reading tracker and the novenas tool.
The theme does not use Astra's header or footer on custom pages. Each page template is a complete, standalone HTML document with its own navigation. Keep this in mind when adding pages (section 6).
2. Hosting and versions
• Host: AWS Lightsail instance running the Lightsail-packaged WordPress blueprint (not Bitnami).
• WordPress: 7.1.5. PHP: 8.3.
• WordPress folder: /var/www/html. wp-config.php sits one level above, in /var/www.
• Web server: Not confirmed from the export (To confirm: apachectl -v).
• Parent theme: Astra 4.13.11 (an update to 4.14.3 was available). Child theme: astra-child 1.0.0, active.
• CDN/cache: Code comments refer to Cloudflare caching the reader page (To confirm the Cloudflare setup, DNS and SSL). WP Super Cache is installed but inactive.
• WP-CLI is available on the server. Run commands from /var/www/html with --allow-root.
• Comments are disabled site-wide in the child theme's functions.php.
Before changing anything: take a Lightsail snapshot (instance management page, Snapshots tab).
3. Plugins
Custom (written for this site):
• Bible Reader (bible-study-notes, v1.1.0): the core. Creates database tables, serves Bible text and notes through a REST API, stores highlights and progress, triggers note generation on GitHub.
• BSN Post Audio (bsn-post-audio.php, v1.5): generates an MP3 for each post.
• Scripture Cross-Reference Explainer (scripture-crossref-ai.php, v1.0): REST endpoint that explains groups of cross-references with OpenAI.
• Scripture Questions (scripture-questions, v1.0): admin tool that drafts Bible Question pages with OpenAI.
• Scripture Reading Tracker (scripture-reading-tracker, v1.1.0): private per-user reading tracker.
• Scripture Novenas (scripture-novenas, v1.0.0): [scripture_novenas] shortcode with eight public-domain novenas.
Third-party (active): Code Snippets (no snippets have been created), WP Mail SMTP, WPS Hide Login (the login page is not at /wp-login.php; the custom login address is kept private and is not recorded here), WP Statistics.
Third-party (inactive): Query Monitor, WP Super Cache.
4. Custom theme (astra-child)
Folder: wp-content/themes/astra-child/
functions.php does the following:
• bsn_logo_icon() outputs the open-book SVG logo used in every nav.
• bsn_page_url_by_template($template_file) finds the permalink of whichever page uses a given template. Navigation links use it, so renaming a page slug does not break the nav, but renaming or moving a template file does.
• Loads the Astra parent stylesheet.
• On the Bible Reader template only: enqueues Google Fonts, assets/reader.css, assets/reader.js and Alpine.js (loaded after reader.js on purpose; do not reorder). It passes BibleReaderConfig (REST base URL and nonce) to the script.
• On the Homepage, Prayer, Reading Order and About templates, and on the blog index, single posts and archives: enqueues assets/homepage.css. A new template that needs the site's standard styling must be added to this condition.
• Registers the bsn_prayer post type and seeds five starter prayers once.
• Disables comments everywhere and removes comment menus.
Templates in the theme root:
• home.php: the Posts page (Devotions). Includes its own search and category filtering through ?s= and ?study_cat=.
• single.php: individual study posts.
• archive.php: date, category, tag and author archives.
Page templates (page-templates/):
• homepage.php: home page; shows a daily verse and the explorer block.
• bible-reader.php: the Bible reader (Alpine.js app).
• prayer.php: today's prayer.
• reading-order.php: curated reading path (hardcoded list).
• about.php: About page (hardcoded text).
• studytools.php: Study Tools hero plus the page's own Custom HTML block.
• verse-refs.php: Verse References hero plus a Custom HTML block that loads a script.
• coverage.php: private Post Coverage page (admin only).
• hompageNAVUpdate.php: an older or alternate copy of the homepage template (see section 8).
Assets: reader.js, reader.css, homepage.css, plus backup copies (see section 8).
5. Custom plugins in detail
Bible Reader (bible-study-notes)
Database tables (created on activation and kept in sync by a version check on every load):
• {prefix}study_notes: one note per book, chapter and verse range.
• {prefix}verse_highlights: highlights per visitor.
• {prefix}chapter_progress: chapters read per visitor.
• {prefix}bible_verses and {prefix}bible_books: the KJV/ASV text and book list. These are built by a separate import script, import-bible.php, which was not in the export (To confirm where it lives).
Visitor identity: logged-in users are u{ID}; everyone else gets an anonymous cookie, bsn_visitor_id, created only when someone first highlights or records progress. This keeps the reader page cookie-free so Cloudflare can cache it. Do not set cookies on page load.
REST API, base /wp-json/bible-study/v1/:
• GET /notes?book=&chapter=: notes for a chapter (public).
• POST /notes: create or replace a note (administrator only).
• GET /books, GET /chapter: Bible structure and text used by the reader.
• GET/POST /highlights, GET/POST /progress, GET /last-read, GET /progress-all: per-visitor features.
• POST /trigger-note: starts a GitHub Actions workflow that generates a study note (administrator only).
• GET/POST /coverage: which chapters already have a published post, kept in the option bsn_chapter_coverage (administrator only).
Automation: a GitHub Actions workflow publishes notes and posts back into WordPress through the REST API using an Application Password (Users > Profile > Application Passwords). The workflow files were not in the export (To confirm: repository name and workflow file names).
BSN Post Audio
When a post is saved (published, draft or pending), it schedules a background WP-Cron job about 30 seconds later. The job sends the text to OpenAI text-to-speech (model tts-1, voice onyx, speed 0.85) and saves an MP3 named after the post slug. The audio URL is stored in post meta _bsn_audio_url and any error in _bsn_audio_error. Audio is generated once per post, so republishing does not trigger a second paid call. An admin menu page shows queue status and errors. If audio fails to save, check that the uploads folder is owned by www-data.
Scripture Cross-Reference Explainer
Public endpoint POST /wp-json/scripture/v1/explain. It validates input (verse, text, up to 25 references), checks a cache (30 days), and applies a rate limit of 20 uncached requests per IP per hour before calling OpenAI. It is used by the Verse References page through crossref-tab.js.
Scripture Questions
Adds the Bible Questions menu (post type sl_question, archive at /questions/, topic taxonomy at /question-topic/). The submenu Ask a Question takes a question and drafts a study page with exact KJV quotes pulled from the site's own database (AJAX action sq_generate). It uses its own templates in the plugin's templates/ folder through the template_include filter.
Scripture Reading Tracker
Shortcode [bible_tracker]. Progress is stored per logged-in user in user meta bibletracker_progress, through the REST route /wp-json/bibletracker/v1/progress. The page holding the shortcode is set to Private.
Scripture Novenas
Shortcode [scripture_novenas] renders a self-contained app (its CSS and JS are printed in the footer only when the shortcode is on the page). No published page in the page export currently uses it (To confirm).
6. How each existing page works
• Home (ID 12), template homepage.php: daily verse (cached in a transient named bsn_votd_YYYY-MM-DD) plus a Custom HTML explorer block, styled by homepage.css.
• Reader (ID 9), bible-reader.php: the Alpine.js reader. No editable content.
• Pray (ID 14), prayer.php: shows one prayer a day from the Prayers post type. Add prayers in wp-admin > Prayers.
• Devotions (ID 16), default template: appears to be the Posts page, rendered by home.php (To confirm in Settings > Reading).
• Study Tools (ID 191), studytools.php: hero in the template, content in the page's Custom HTML block.
• Reading Order (ID 71), reading-order.php: the book list is a PHP array in the template. Edit the file to change it.
• Verse References (ID 781), verse-refs.php: Custom HTML block that loads /wp-content/uploads/crossrefs/crossref-tab.js. That script is not in the theme or plugins and was not in the export (To confirm).
• About (ID 101), about.php: text is hardcoded in the template.
• Bible Reading Tracker (ID 203, private): contains [bible_tracker] but is assigned the coverage.php template (To confirm this is intended).
• Privacy Policy (ID 3, draft): still the WordPress default text.
7. How to add a new page
Option A: a normal content page. Pages > Add New, write the content, publish. This uses Astra's default layout, so it will show Astra's header and not the site's custom navigation. Fine for utility pages, but it will look different.
Option B: a page that matches the site (recommended).
1.  Snapshot first (section 2).
2.  Copy a template in wp-content/themes/astra-child/page-templates/:
    ◦ Simple text page: copy about.php.
    ◦ Hero banner with editable content below: copy studytools.php (it has its own inline CSS, so it does not depend on homepage.css).
3.  Edit the copy: change the Template Name: line at the top (this is the name shown in the page editor), the <title>, and the body_class.
4.  If the copy uses homepage.css styling (like about.php), add the new template's path to the condition in the Homepage-specific styles block in functions.php. If you skip this, the page appears unstyled.
5.  Create the page: Pages > Add New, set Template to your new template in Page Attributes, add content, publish.
6.  Add it to the navigation. Navigation is built in each template rather than in one place. Search the theme for about_url to find every template that builds the nav (home.php, single.php, archive.php, homepage.php and others), then add a matching URL variable and link in each. Use bsn_page_url_by_template() rather than hardcoding the slug.
7.  Check the page logged out, on mobile, and after clearing any Cloudflare cache.
Page that needs data or interactivity: add a REST route or shortcode in a plugin (not the theme), and load scripts only on that template, following the pattern used for the reader in functions.php.
8. Gotchas and cleanup
• Backup files in public folders. The theme and plugin folders contain backup copies (for example .bak files for the main plugin, reader.BFMoveNotePlane.js.bk, hompage_backup.css, archive_backup.php, common_backup.php, a hidden .reader.js, and a scripture-questions.zip in the plugins folder). Move them out of the web root. Never edit one thinking it is live. The live files are the ones named in this guide.
• Two templates named "Homepage". homepage.php and hompageNAVUpdate.php both declare Template Name: Homepage. The Home page uses homepage.php. Rename or remove the other to avoid picking the wrong one.
• Duplicate block on Verse References. The page content contains the same slVerseRefs block twice (one loading crossref-tab.js?v=2, one ?v=4). Remove the old one.
• Privacy Policy still contains the default text with http://127.0.0.1 in it. Replace it before publishing.
• Secrets live outside the code. API keys and GitHub credentials are defined in wp-config.php, not in plugin files. Keep it that way. Never commit or share wp-config.php.
• Template renames break navigation because links are resolved from template file names.
• Cloudflare caching: pages must not send cookies on load or they will stop being cached.
• Updates: update Astra on a snapshot copy first, since the child theme depends on it. Several plugins have auto-update turned off on purpose; check before turning it on for the custom ones (they have no update source).
• Bible text tables are not rebuilt by WordPress. If the database is restored without them, the reader and home page verse will break.
9. Configuration reference (names only, no values)
Defined in wp-config.php:
• OPENAI_API_KEY: cross-reference explainer and Scripture Questions.
• BSN_OPENAI_API_KEY (or the environment variable OPENAI_API_KEY): post audio.
• SCE_MODEL, SQ_MODEL, SQ_STYLE_NOTES: optional model and style settings.
• BSN_GITHUB_TOKEN, BSN_GITHUB_OWNER, BSN_GITHUB_REPO, BSN_GITHUB_WORKFLOW_FILE: used by /trigger-note.
Stored in the database: options bsn_db_version, bsn_prayers_seeded, bsn_chapter_coverage; user meta bibletracker_progress; post meta _bsn_audio_url and _bsn_audio_error; transients for the daily verse, cross-reference cache and rate limits.
10. Items to fill in
These were not available in the export. Add them before handing this guide to a developer:
• Location and contents of import-bible.php and crossref-tab.js.
• GitHub repository and workflow file names for note and post generation.
• DNS provider, Cloudflare settings, SSL method and Lightsail static IP.
• Backup and snapshot schedule.
• Where the credentials are kept and who has access (do not write them in this document).