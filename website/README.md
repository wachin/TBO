# The project site

Static site for TBO 2, published by [`.github/workflows/deploy-website.yml`](../.github/workflows/deploy-website.yml)
to <https://wachin.github.io/TBO/>.

No build step and no external requests: `index.html`, `styles.css`, `favicon.svg`,
`sitemap.xml` and the files under `images/`. Open `index.html` straight from disk
and it works.

| Path | What it is |
|---|---|
| `index.html` | The whole site. One page, sections linked from the header nav. |
| `styles.css` | All styling. Dark theme, no framework, no CDN. |
| `sitemap.xml` | One URL. Submitted to Google Search Console by hand (below). |
| `images/TBO2-en-ezgif.com.gif` | The demo recording, 800×451, 30 s, 554 KB. |
| `images/social-card.png` | 1200×630 link-preview card. |
| `tools/make_social_card.py` | Regenerates `social-card.png` with Pillow. |

## Search engines

`index.html` carries the pieces a crawler needs: a `<title>` and description, a
canonical URL, Open Graph and Twitter card tags, `max-image-preview:large`, and
JSON-LD describing the app as a `SoftwareApplication`. That is the part that can
be done in the repository. **Being indexed is not something the repository can
do** — it needs a one-time action from whoever owns the Google account:

1. Open [Google Search Console](https://search.google.com/search-console) and add
   a property. Use **URL prefix**, not *Domain*: `https://wachin.github.io/TBO/`.
   A *Domain* property needs DNS control of `wachin.github.io`, which belongs to
   GitHub, not to this project.
2. Verify it with the **HTML tag** method. Search Console gives a
   `<meta name="google-site-verification" content="...">` tag; paste it into
   `index.html`'s `<head>`, commit, push, wait for the deploy, then press Verify.
   The token is not a secret, but it is per-account, so it is deliberately not
   committed here.
3. Under **Sitemaps**, submit `sitemap.xml`. Then use **URL inspection** on
   `https://wachin.github.io/TBO/` and press *Request indexing*.

Indexing takes days, not minutes, and *Request indexing* only asks for a
recrawl — it is not a switch. Nothing about this can be forced from the
repository side.

There is deliberately **no `robots.txt`**. Google fetches it only from the root
of a host, and this site sits on GitHub's shared `wachin.github.io` domain at a
`/TBO/` subpath, so a file here would never be read. Adding one would look like
crawl configuration while changing nothing.

## The two copies of the demo GIF

`images/TBO2-en-ezgif.com.gif` exists at the repository root **and** under
`website/images/`. That is on purpose, and both must be replaced together:

- the root copy is what `README.md` embeds on GitHub;
- the `website/` copy is what the Pages workflow publishes, because the workflow
  uploads only the `website` directory.

Keeping the site's copy local to `website/` is what lets the page work from disk.
The alternative — copying assets around inside the workflow — would hide the
dependency in CI instead of showing it in the tree.

## Regenerating the preview card

```bash
python3 website/tools/make_social_card.py
```

Needs Pillow and numpy. It draws the card from a real frame of the demo GIF, and
measures the text before placing it so the headline cannot run under the
screenshot. Delete the PNG and the command above is the only way it comes back.
