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
| `google28242c9a5701a052.html` | Proof of ownership for Google Search Console. **Do not touch.** |

### `google28242c9a5701a052.html`

This one deserves its own warning, because it looks exactly like the kind of
stray build artefact a tidy-minded contributor deletes.

It is the ownership proof for the Search Console property
`https://wachin.github.io/TBO/`, and it has to stay **at the site root, with
these exact 53 bytes**:

```
google-site-verification: google28242c9a5701a052.html
```

No trailing newline. Google fetches
<https://wachin.github.io/TBO/google28242c9a5701a052.html> and compares the
body character for character, so reformatting it, renaming it, moving it into a
subdirectory, or "fixing" the missing newline at the end of the file all break
verification and can take the property — and its sitemap submission — with it.
The file is not a secret and is public by design; anyone can fetch it.

## Search engines

`index.html` carries the pieces a crawler needs: a `<title>` and description, a
canonical URL, Open Graph and Twitter card tags, `max-image-preview:large`, and
JSON-LD describing the app as a `SoftwareApplication`. That is the part that can
be done in the repository.

Ownership of the property was proved with the **HTML file** method rather than
the meta tag, because the file needs no edit to `index.html` and survives any
future rewrite of the head. The remaining work is a one-time manual step in
Google Search Console, which no commit can do:

1. The property already exists, as **URL prefix**
   `https://wachin.github.io/TBO/`. A *Domain* property was not used and could
   not be: that method needs a DNS TXT record on `github.io`, which belongs to
   GitHub.
2. Under **Sitemaps**, submit `sitemap.xml`.
3. Use **URL inspection** on `https://wachin.github.io/TBO/` and press *Request
   indexing*.

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
